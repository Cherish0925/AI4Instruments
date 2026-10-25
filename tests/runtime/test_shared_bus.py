"""Several logical instruments use one physical bus throughout configuration changes."""
import copy
import importlib.util
import socketserver
import struct
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch
from ai4instruments.iop import IOPError
from ai4instruments.iop.adapters import Modbus
from . import test_service as fixture


class BusInstrument(socketserver.StreamRequestHandler):
    def handle(self):
        self.server.connections += 1
        while header := self.rfile.read(7):
            tid, _, size, unit = struct.unpack('>HHHB', header)
            pdu = self.rfile.read(size - 1)
            self.server.requests.append(unit)
            self.server.entered.set()
            self.server.release.wait(5)
            address, count = struct.unpack('>HH', pdu[1:])
            body = bytes([3, count * 2]) + struct.pack('>' + 'H' * count, *[unit * 100 + address] * count)
            self.wfile.write(struct.pack('>HHHB', tid, 0, len(body) + 1, unit) + body)
            self.wfile.flush()


class SharedBusCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def bus(self):
        server = socketserver.ThreadingTCPServer(('127.0.0.1', 0), BusInstrument)
        server.daemon_threads = True
        server.requests, server.connections = [], 0
        server.entered, server.release = threading.Event(), threading.Event()
        server.release.set()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return server

    def register(self, server, name, unit):
        record = {'id': name, 'driver': 'modbus', 'config': {
            'host': '127.0.0.1', 'port': server.server_address[1], 'device_id': unit,
            'operations': {'temperature': {'function': 'read_holding_registers',
                'arguments': {'address': 1, 'count': 1}, 'scale': 0.1, 'unit': 'degC'}}}}
        self.client.register(record)
        return record

    def read(self, device):
        return self.client.submit([{'id': 'read', 'device': device, 'operation': 'temperature'}])

    @unittest.skipUnless(importlib.util.find_spec('pymodbus'), 'Install the devices extra for Modbus communication')
    def test_configuring_one_unit_preserves_the_other_connection(self):
        server = self.bus()
        a = self.register(server, 'a', 1)
        self.register(server, 'b', 2)
        self.assertAlmostEqual(self.read('a').result(3)['read']['value'], 10.1)
        self.assertAlmostEqual(self.read('b').result(3)['read']['value'], 20.1)
        socket = self.engine.devices['b'].connection
        a['config']['name'] = 'Temperature channel'
        self.client.configure_device('a', a, self.client.device_history('a')[0]['revision'])
        self.assertIs(socket, self.engine.devices['b'].connection)
        self.assertTrue(socket.connected)
        self.assertAlmostEqual(self.read('a').result(3)['read']['value'], 10.1)
        self.assertAlmostEqual(self.read('b').result(3)['read']['value'], 20.1)
        self.assertEqual(server.connections, 1)
        self.assertEqual(server.requests, [1, 2, 1, 2])

    def test_discovery_retains_every_device_on_a_shared_serial_connection(self):
        from ai4instruments.iop.discovery import normalize
        for unit in (1, 2):
            self.client.register({'id': 'serial-' + str(unit), 'driver': 'modbus',
                                  'config': {'transport': 'serial', 'port': 'COM7', 'device_id': unit}})
        inventory = normalize({'connections': [{'transport': 'serial', 'address': 'COM7', 'provider': 'serial'}],
                               'providers': [{'name': 'serial', 'available': True}]})
        with patch('ai4instruments.iop.discovery.discover', return_value=inventory):
            result = self.engine.scan()
        group = result['groups'][0]
        self.assertEqual(group['device_ids'], ['serial-1', 'serial-2'])
        self.assertNotIn('id', group)
        self.assertEqual(result['instruments'][0]['device_ids'], ['serial-1', 'serial-2'])
        self.assertEqual(result['instruments'][0]['required'], [])
        self.assertTrue(self.engine.device_states()['serial-1']['present'])
        self.assertTrue(self.engine.device_states()['serial-2']['present'])

    def test_device_addresses_are_distinct_and_operations_keep_their_address(self):
        server = self.bus()
        record = self.register(server, 'a', 1)
        other = self.register(server, 'b', 2)
        with self.assertRaisesRegex(IOPError, 'already belongs'):
            self.client.register(dict(record, id='duplicate'))
        wrong = copy.deepcopy(other)
        wrong['config']['device_id'] = 1
        with self.assertRaises(IOPError) as error:
            self.client.configure_device('b', wrong, self.client.device_history('b')[0]['revision'])
        self.assertEqual(error.exception.code, 'connection_in_use')
        with self.assertRaises(IOPError):
            self.client.submit([{'id': 'wrong', 'device': 'a', 'operation': 'read_holding_registers',
                                'arguments': {'address': 0, 'device_id': 2}}])
        self.assertEqual(server.requests, [])

    @unittest.skipUnless(importlib.util.find_spec('pymodbus'), 'Install the devices extra for Modbus communication')
    def test_tcp_accepts_zero_and_255_unit_identifiers(self):
        server = self.bus()
        for unit in (0, 255):
            device = 'tcp-' + str(unit)
            self.register(server, device, unit)
            self.assertAlmostEqual(self.read(device).result(3)['read']['value'], (unit * 100 + 1) * 0.1)
        self.assertEqual(server.requests, [0, 255])
        self.assertEqual(server.connections, 1)

    @unittest.skipUnless(importlib.util.find_spec('pymodbus'), 'Install the devices extra for Modbus communication')
    def test_shared_bus_serializes_requests_and_another_bus_continues(self):
        first, second = self.bus(), self.bus()
        self.register(first, 'a', 1)
        self.register(first, 'b', 2)
        self.register(second, 'c', 1)
        first.release.clear()
        try:
            a = self.read('a')
            self.assertTrue(first.entered.wait(2))
            b = self.read('b')
            self.assertAlmostEqual(self.read('c').result(2)['read']['value'], 10.1)
            self.assertEqual(first.requests, [1])
            self.assertEqual(b.info()['operation_records'][0]['state'], 'queued')
        finally:
            first.release.set()
        a.result(3); b.result(3)
        self.assertEqual(first.requests, [1, 2])
        self.assertEqual(first.connections, 1)

    @unittest.skipUnless(importlib.util.find_spec('pymodbus'), 'Install the devices extra for Modbus communication')
    def test_editing_idle_unit_does_not_close_an_active_neighbour(self):
        server = self.bus()
        a = self.register(server, 'a', 1)
        self.register(server, 'b', 2)
        self.read('a').result(3)
        server.entered.clear(); server.release.clear()
        pool = ThreadPoolExecutor(1)
        try:
            b = self.read('b')
            self.assertTrue(server.entered.wait(2))
            a['config']['name'] = 'Updated name'
            edit = pool.submit(self.client.configure_device, 'a', a, self.client.device_history('a')[0]['revision'])
            time.sleep(0.05)
            server.release.set()
            self.assertAlmostEqual(b.result(3)['read']['value'], 20.1)
            self.assertEqual(edit.result(3)['definition']['config']['name'], 'Updated name')
            self.assertAlmostEqual(self.read('a').result(3)['read']['value'], 10.1)
            self.assertEqual(server.connections, 1)
        finally:
            server.release.set(); pool.shutdown()


@unittest.skipUnless(importlib.util.find_spec('pymodbus'), 'Install the devices extra for Modbus communication')
class SerialBusCase(unittest.TestCase):
    def test_one_serial_handle_per_bus_and_each_unit_uses_its_own_timeout(self):
        class Client:
            def __init__(self, port, **options):
                self.comm_params = SimpleNamespace(timeout_connect=options['timeout'])
                self.socket = SimpleNamespace(timeout=options['timeout'], write_timeout=options['timeout'])
                self.closed = False
            def connect(self): return True
            def close(self): self.closed = True
            def read_holding_registers(self, **values):
                return SimpleNamespace(isError=lambda: False, registers=[values['device_id']])
        registry = {}
        with patch('pymodbus.client.ModbusSerialClient', side_effect=Client) as factory:
            a = Modbus('a', {'transport': 'serial', 'port': 'COM7', 'device_id': 1, 'timeout': 1}, registry)
            registry['a'] = a
            b = Modbus('b', {'transport': 'serial', 'port': 'com7', 'device_id': 2, 'timeout': 5}, registry)
            registry['b'] = b
            args = {'address': 0, 'count': 1}
            a.invoke('read_holding_registers', args, threading.Event())
            handle = a.connection
            b.invoke('read_holding_registers', args, threading.Event())
            self.assertEqual(handle.socket.timeout, 5)
            self.assertIs(a.connection, b.connection)
            self.assertEqual(factory.call_count, 1)
            with self.assertRaisesRegex(ValueError, 'same serial settings'):
                Modbus('bad', {'transport': 'serial', 'port': 'COM7', 'baudrate': 9600}, registry)
            a.close(); a.close()
            self.assertFalse(handle.closed)
            self.assertEqual(b.invoke('read_holding_registers', args, threading.Event())['value'], 2)
            b.close()
            self.assertTrue(handle.closed)
