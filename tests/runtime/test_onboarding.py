"""Shared instrument setup and data access, independent of a particular model."""
import copy
import json
import socketserver
import sqlite3
from ai4instruments.iop import Driver
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from ai4instruments.iop.discovery import discover, normalize, match_profiles
from ai4instruments.iop.drivers import SCPI
from . import test_service as fixture


class Recorded(Driver):
    def describe(self):
        return {'mode': 'simulation', 'operations': {'read': {'parameters': {}}}}

    def invoke(self, operation, arguments, context):
        with sqlite3.connect(self.config['database']) as db:
            state, = db.execute('SELECT state FROM operations WHERE id=?', (context.operation_id,)).fetchone()
        if state != 'running':
            raise RuntimeError('Operation started before its record was committed')
        return {'value': 1}


class SetupCase(unittest.TestCase):
    def setUp(self):
        fixture.ServiceCase.setUp(self)
        self.engine.discovery_stop.set()
        if self.engine.discovery_thread:
            self.engine.discovery_thread.join(10)
    tearDown = fixture.ServiceCase.tearDown

    def test_grouped_starts_commit_before_calls_and_retry_a_failed_write(self):
        records = [{'id': 'recorded-' + str(i), 'driver': __name__ + ':Recorded',
                    'config': {'database': str(self.engine.home / 'records.sqlite3')}} for i in range(6)]
        self.client.register_many(records)
        original = self.engine.store.put
        failures = []
        def put(table, item):
            if table == 'operations' and item['state'] == 'running' and not failures:
                failures.append(item['id'])
                raise OSError('Simulated write interruption')
            return original(table, item)
        with patch.object(self.engine.store, 'put', side_effect=put):
            run = self.client.submit([{'id': r['id'], 'device': r['id'], 'operation': 'read'} for r in records])
            self.assertEqual(len(run.result(5)), 6)
        self.assertEqual(len(failures), 1)
        started = [e for e in self.client.events(run_id=run.id)['events'] if e['kind'] == 'operation.started']
        self.assertEqual(len(started), 6)
        self.assertEqual(len({e['operation_id'] for e in started}), 6)

    def test_generated_id_is_saved_and_reused_by_all_clients(self):
        record = {'driver': 'scpi', 'config': {'name': '温度仪', 'transport': 'serial', 'port': 'COM12'}}
        original = copy.deepcopy(record)
        first = self.client.register(record)
        driver = self.engine.devices[first['id']]
        self.assertRegex(first['id'], r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$')
        self.assertEqual(first, self.client.register(record))
        self.assertIs(driver, self.engine.devices[first['id']])
        saved = json.loads((self.engine.home / 'config.json').read_text())
        self.assertIn(first['id'], [d['id'] for d in saved['devices']])
        self.assertEqual(record, original)

    def test_batch_reports_each_item_without_losing_successful_items(self):
        records = [{'driver': 'simulated', 'id': 'new-axis'}, {'driver': 'missing-driver'},
                   {'driver': 'simulated', 'id': 'new-meter', 'config': {'kind': 'meter'}}]
        rows = self.client.register_many(records)['results']
        self.assertEqual([r['index'] for r in rows], [0, 1, 2])
        self.assertIn('error', rows[1])
        self.assertEqual(rows[2]['device']['id'], 'new-meter')
        self.assertTrue({'new-axis', 'new-meter'} <= self.engine.devices.keys())

    def test_background_scan_is_shared_and_does_not_hold_up_experiments(self):
        entered, release = threading.Event(), threading.Event()
        def inventory(*_):
            entered.set()
            if not release.wait(5):
                raise TimeoutError('scan was not released')
            return {'connections': [], 'providers': []}
        with patch('ai4instruments.iop.discovery.discover', side_effect=inventory) as scan:
            try:
                self.assertTrue(self.client.start_discovery()['scanning'])
                self.assertTrue(entered.wait(2))
                self.assertTrue(self.client.start_discovery()['scanning'])
                self.assertTrue(self.client.inventory()['scanning'])
                self.client.submit([{'id': 'position', 'device': 'stage', 'operation': 'position'}]).result(3)
                self.assertEqual(scan.call_count, 1)
            finally:
                release.set()
                if self.engine.scan_request:
                    self.engine.scan_request.join(3)
        self.assertFalse(self.client.inventory()['scanning'])

    def test_known_serial_visa_alias_cannot_open_two_drivers(self):
        with patch('ai4instruments.iop.discovery.platform.system', return_value='Windows'):
            self.client.register({'id': 'serial-device', 'driver': 'scpi', 'config': {'transport': 'serial', 'port': 'com9'}})
            from ai4instruments.iop import IOPError
            with self.assertRaisesRegex(IOPError, 'already belongs'):
                self.client.register({'id': 'duplicate', 'driver': 'scpi', 'config': {'transport': 'visa', 'resource': 'ASRL9::INSTR'}})

    def test_operation_wait_and_small_run_summary(self):
        run = self.client.submit([{'id': 'wait', 'device': 'stage', 'operation': 'wait', 'arguments': {'duration': 0.15}}])
        operation = run.operations()['operations'][0]
        done = self.client.request('/v1/operations/' + operation['id'] + '?wait=3')
        self.assertEqual(done['state'], 'completed')
        run.result(5)
        record = self.engine.store.get('runs', run.id)
        record['result'] = {'data': 'x' * 1000000}
        with self.engine.store.transaction():
            self.engine.store.put('runs', record)
        summary = run.info(details=False)
        self.assertNotIn('result', summary)
        self.assertNotIn('operations', summary)
        self.assertNotIn('definition', summary)
        self.assertLess(len(json.dumps(summary)), 3000)
        self.assertNotIn('result', self.client.request('/v1/runs?details=false')[0])
        self.assertEqual(len(self.client.request('/v1/runs/' + run.id + '/result')['data']), 1000000)


class DiscoveryCase(unittest.TestCase):
    def test_independent_providers_run_concurrently(self):
        ready = threading.Barrier(4)
        def provider(*_):
            ready.wait(3)
            return [], []
        with patch('ai4instruments.iop.discovery._serial', side_effect=provider), \
             patch('ai4instruments.iop.discovery._visa', side_effect=provider), \
             patch('ai4instruments.iop.discovery._usb', side_effect=provider), \
             patch('ai4instruments.iop.discovery._software', side_effect=provider):
            self.assertEqual(discover()['connections'], [])

    def test_inventory_groups_aliases_but_keeps_distinct_interfaces(self):
        rows = [{'transport': 'serial', 'address': 'COM7'}, {'transport': 'visa', 'address': 'ASRL7::INSTR'},
                {'transport': 'serial', 'address': 'COM8'}, {'transport': 'usb', 'address': 'USB-keyboard'}]
        with patch('ai4instruments.iop.discovery.platform.system', return_value='Windows'):
            result = normalize({'connections': rows})
        self.assertEqual(result['summary'], {'interfaces': 2, 'usb_entries': 1})
        self.assertEqual(len(result['connections']), 4)
        self.assertEqual(len(result['groups'][0]['interfaces']), 2)

    def test_profiles_preserve_operation_templates_and_match_usb_identifiers(self):
        inventory = {'connections': [{'transport': 'serial', 'address': 'COM7', 'vid': 6790, 'pid': 29987}]}
        profiles = [{'match': {'transport': 'serial', 'vid': '0x1a86', 'pid': '7523'},
                     'device': {'driver': 'scpi', 'config': {'port': '{address}', 'operations': {'set': {'write': 'VOLT {value:.3f}'}}}}}]
        record, = match_profiles(inventory, profiles)
        self.assertEqual(record['config']['port'], 'COM7')
        self.assertEqual(record['config']['operations']['set']['write'], 'VOLT {value:.3f}')


class StreamCase(unittest.TestCase):
    def test_fragmented_large_response_and_queued_line_preserve_framing(self):
        payload = b'1.234,' * 30000
        class Instrument(socketserver.StreamRequestHandler):
            def handle(self):
                while True:
                    line = self.rfile.readline()
                    if not line:
                        return
                    if line == b'DATA?\r\n':
                        self.wfile.write(payload + b'\r')
                        self.wfile.flush()
                        self.wfile.write(b'\nsecond\r\n')
                        self.wfile.flush()
                    elif line == b'*IDN?\r\n':
                        self.wfile.write(b'Example,Reader,SN123,1.0\r\n')
                        self.wfile.flush()
        server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), Instrument)
        server.daemon_threads = True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        driver = SCPI('reader', {'host': '127.0.0.1', 'port': server.server_address[1], 'termination': '\r\n'}, {})
        try:
            self.assertEqual(driver.exchange('DATA?', True), payload.decode())
            self.assertEqual(driver.exchange('NEXT?', True), 'second')
            result = driver.invoke('identify', {}, threading.Event())
            self.assertEqual(result['identity']['serial_number'], 'SN123')
            self.assertEqual(result['value'], 'Example,Reader,SN123,1.0')
        finally:
            driver.close()
            server.shutdown()
            server.server_close()
