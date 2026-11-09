"""Continuous experiments, stored acquisitions and explicit connection handover."""
import copy
import json
import os
import subprocess
import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from ai4instruments.iop import Client, Driver, IOPError
from ai4instruments.iop.drivers import SCPI
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.identification import parse_identity
from ai4instruments.iop.server import Server
from . import test_service as fixture
from . import test_identification


class SharedWorker(Driver):
    def __init__(self, device_id, config, registry):
        super().__init__(device_id, config, registry)
        self.worker = next((d.worker for d in registry.values() if isinstance(d, SharedWorker)), None)
        if self.worker is None:
            self.worker = {'closed':False}

    def describe(self):
        return {'operations':{'read':{'parameters':{}}}}

    def invoke(self, operation, arguments, cancelled):
        if self.worker['closed']:
            raise RuntimeError('Worker is closed')
        return {'value':1}

    def close(self):
        self.worker['closed'] = True


class ContinuityCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    instrument = test_identification.IdentificationCase.instrument
    scan = test_identification.IdentificationCase.scan

    def step(self, name, device='stage', after=None):
        value = {'id':name, 'device':device, 'operation':'position'}
        if after is not None:
            value['after'] = after
        return value

    def restart(self):
        self.server.shutdown(); self.server.server_close(); self.engine.close()
        self.config = json.loads((self.engine.home/'config.json').read_text())
        self.engine = Engine(self.temp.name, self.config)
        self.server = Server(('127.0.0.1',0), self.engine)
        self.engine.start()
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.client.endpoint = self.engine.endpoint

    def test_sequence_is_atomic_and_retry_never_reexecutes(self):
        run = self.client.start_experiment(resources=['stage'])
        steps = [{'id':'move','device':'stage','operation':'move_to','arguments':{'angle_deg':23}}, self.step('read')]
        first = run.batch(steps, request_id='point-23', timeout=3)
        self.assertEqual(first[1]['result']['angle_actual'], 23)
        self.assertLessEqual(first[0]['ended'], first[1]['started'])
        second = run.batch(steps, request_id='point-23', timeout=3)
        self.assertEqual([op['id'] for op in first], [op['id'] for op in second])
        with self.assertRaises(IOPError):
            run.batch([self.step('other')], request_id='point-23')
        run.finish()
        self.assertEqual(run.batch(steps, request_id='point-23')[0]['id'], first[0]['id'])
        self.assertEqual(len(run.operations()['operations']), 2)

    def test_invalid_batch_accepts_no_operations(self):
        run = self.client.start_experiment()
        for steps in ([self.step('read'), dict(self.step('bad'), operation='missing')],
                      [self.step('one', after=['two']), self.step('two', after=['one'])], [1]):
            with self.assertRaises(IOPError):
                run.batch(steps)
        self.assertEqual(run.operations()['operations'], [])
        self.assertEqual(run.info(False)['operation_count'], 0)
        run.finish()

    def test_parallel_branches_join_and_bind_completed_results(self):
        with self.client.start_experiment(resources=['stage','aux']) as run:
            steps = [{'id':name,'device':device,'operation':'wait','arguments':{'duration':0.2},'after':[]}
                     for name, device in [('a','stage'), ('b','aux')]]
            steps.append({'id':'join','device':'stage','operation':'move_to','after':['a','b'],
                          'bindings':{'angle_deg':{'step':'a','path':['elapsed_s']}}})
            ops = run.batch(steps, request_id='parallel-join', timeout=4)
            self.assertLess(ops[0]['started'], ops[1]['ended'])
            self.assertLess(ops[1]['started'], ops[0]['ended'])
            self.assertGreaterEqual(ops[2]['started'], max(ops[0]['ended'], ops[1]['ended']))
            self.assertEqual(ops[2]['result']['angle_actual'], 0.2)
            with self.engine.lock:
                self.assertEqual(self.engine.dependents, {})
                self.assertEqual(self.engine.remaining_dependencies, {})
                self.assertEqual(self.engine.operations, {})

    def test_many_batches_keep_scheduler_memory_bounded(self):
        with self.client.start_experiment() as run:
            for i in range(20):
                run.batch([self.step('a'), self.step('b')], request_id=f'batch-{i}')
            with self.engine.lock:
                self.assertEqual(self.engine.operations, {})
                self.assertEqual(self.engine.dependents, {})
                self.assertEqual(self.engine.remaining_dependencies, {})
            self.assertEqual(run.info(False)['operation_count'], 40)

    def test_failure_cancels_batch_dependents(self):
        self.client.register({'id':'absent','driver':'scpi','config':{'host':'127.0.0.1','port':1,'timeout':0.1}})
        run = self.client.start_experiment()
        with self.assertRaises(IOPError):
            run.batch([dict(self.step('fail','absent'), operation='identify'), self.step('read')], timeout=4)
        self.assertEqual(run.wait(3)['state'], 'failed')
        self.assertEqual([o['state'] for o in run.operations()['operations']], ['failed','cancelled'])
        self.assertEqual(self.engine.metrics()['errors'], [])

    def test_acquisition_saves_exact_results_without_reading_again(self):
        with self.client.start_experiment(resources=['stage']) as run:
            op = run.invoke_record('stage', 'position')
            run.invoke('stage', 'move_to', {'angle_deg':42})
            with patch.object(self.engine.devices['stage'], 'invoke', side_effect=AssertionError('unexpected read')):
                saved = run.save_acquisition('first.json', [op['id']], conditions={'sample':'A'}, analysis={'accepted':True})
                again = run.save_acquisition('first.json', [op['id']], conditions={'sample':'A'}, analysis={'accepted':True})
            self.assertEqual(saved['id'], again['id'])
            data = json.loads(self.client.request('/v1/artifacts/'+saved['id'], binary=True))
            self.assertEqual(data['operations'][0]['result'], op['result'])
            self.assertEqual(data['operations'][0]['result']['angle_actual'], 0)
            self.assertEqual(data['device_configurations']['stage@'+str(op['device_revision'])]['revision'], op['device_revision'])
            self.assertEqual(data['analysis'], {'accepted':True})
            self.assertEqual(saved['operation_ids'], [op['id']])
            with self.assertRaises(IOPError):
                run.save_acquisition('first.json', [op['id']], analysis={'accepted':False})

    def test_foreign_acquisition_is_rejected(self):
        with self.client.start_experiment() as first, self.client.start_experiment() as second:
            op = first.invoke_record('stage', 'position')
            with self.assertRaises(IOPError):
                second.save_acquisition('foreign.json', [op['id']])
            self.assertEqual(second.files(), [])

    def test_persistent_http_reuses_socket_and_supports_concurrent_clients(self):
        for _ in range(5):
            self.client.devices()
        with self.server.connection_lock:
            self.assertEqual(len(self.server.connections), 1)
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: self.client.devices(), range(20)))
        with self.client.start_experiment(resources=['stage']) as run:
            with ThreadPoolExecutor(max_workers=4) as pool:
                ops = list(pool.map(lambda i: run.invoke_record('stage','position', request_id=f'r{i}'), range(12)))
            ordered = sorted(ops, key=lambda op:op['started'])
            self.assertEqual(len({op['id'] for op in ops}),12)
            for left, right in zip(ordered, ordered[1:]):
                self.assertLessEqual(left['ended'], right['started'])

    def test_release_rejects_active_work_and_persists_without_opening_driver(self):
        run = self.client.start_experiment(resources=['stage'])
        run.invoke('stage', 'position')
        with self.assertRaises(IOPError):
            self.client.release('stage')
        run.finish()
        self.assertEqual(self.client.release('stage')['state'], 'released')
        with self.assertRaises(IOPError) as error:
            self.client.invoke('stage','position')
        self.assertEqual(error.exception.code, 'device_released')
        from ai4instruments.iop.drivers import make_driver
        def make(record, registry):
            self.assertNotEqual(record['id'], 'stage')
            return make_driver(record, registry)
        with patch('ai4instruments.iop.engine.make_driver', side_effect=make):
            self.restart()
        self.assertEqual(self.client.request('/v1/devices/stage')['status']['state'], 'released')
        self.client.reconnect('stage')
        self.assertEqual(self.client.invoke('stage','position')['angle_actual'], 0)

    def test_whole_quoted_and_individually_quoted_identities(self):
        for response in ('"Vendor,Model,S123,1.2"', 'Vendor,Model,S123,1.2', '"Vendor","Model","S123","1.2"'):
            self.assertEqual(parse_identity(response)['model'], 'Model')
        self.assertEqual(parse_identity('"Vendor, Inc.",Model,S123,1.2')['manufacturer'], 'Vendor, Inc.')
        server, row = self.instrument()
        server.identity = '"Stanford_Research_Systems,SR830,001,1.0"'
        self.assertEqual(self.scan([row])['instruments'][0]['status'], 'ready')
        self.assertEqual(server.commands, ['*IDN?'])

    def test_applying_new_configuration_reconnects_released_instrument(self):
        self.client.release('stage')
        previous = self.client.device_history('stage')[0]
        definition = copy.deepcopy(previous['definition'])
        definition['config']['name'] = 'Updated stage'
        self.client.configure_device('stage', definition, previous['revision'])
        self.assertEqual(self.client.request('/v1/devices/stage')['status']['state'], 'ready')
        self.assertEqual(self.client.invoke('stage','position')['angle_actual'], 0)
        self.restart()
        self.assertEqual(self.client.request('/v1/devices/stage')['name'], 'Updated stage')
        self.assertEqual(self.client.request('/v1/devices/stage')['status']['state'], 'ready')

    def test_shared_worker_handover_reconnects_the_whole_group_after_restart(self):
        for name in ('channel-a','channel-b'):
            self.client.register({'id':name,'driver':__name__+':SharedWorker'})
        self.assertEqual(self.client.release('channel-a')['devices'], ['channel-a','channel-b'])
        self.restart()
        self.assertEqual(self.client.reconnect('channel-b')['devices'], ['channel-a','channel-b'])
        self.assertIs(self.engine.devices['channel-a'].worker, self.engine.devices['channel-b'].worker)
        self.assertEqual(self.client.invoke('channel-a','read'), {'value':1})
        self.assertEqual(self.client.invoke('channel-b','read'), {'value':1})

    def test_unparsed_identity_preserves_reply_without_repeated_queries(self):
        server, row = self.instrument()
        server.identity = 'Unstructured model reply'
        first = self.scan([row])['instruments'][0]
        second = self.scan([row])['instruments'][0]
        self.assertEqual(first['status'], 'identity_unparsed')
        self.assertEqual(second['identity_response'], server.identity)
        self.assertEqual(second['communication'], 'responded')
        self.assertEqual(server.commands, ['*IDN?'])
        self.engine.enrollment.retry(first['key'])
        self.scan([row])
        self.assertEqual(server.commands, ['*IDN?','*IDN?'])

    def test_registered_unparsed_identity_is_a_completed_exchange(self):
        server, row = self.instrument()
        server.identity = 'unstructured'
        device = self.client.register({'id':'odd','driver':'scpi','config':row['connection']})['id']
        response = self.client.invoke(device, 'identify')
        self.assertEqual(response['value'], 'unstructured')
        self.assertIn('identity_error', response)
        self.assertEqual(self.client.request('/v1/devices/odd')['status']['communication']['state'], 'completed')
        self.client.release(device)
        self.scan([row]); self.scan([row])
        self.assertEqual(server.commands, ['*IDN?'])

    def test_scpi_source_address_is_used_and_serial_settings_are_discoverable(self):
        for address in (123, 'not-an-address'):
            with self.assertRaises(ValueError):
                SCPI('network', {'host':'192.0.2.2','source_address':address}, {})
        driver = SCPI('network', {'host':'192.0.2.2','source_address':'192.0.2.1'}, {})
        with patch('socket.create_connection') as connect:
            driver.connect()
        self.assertEqual(connect.call_args.kwargs['source_address'], ('192.0.2.1', 0))
        params = next(a for a in self.client.adapters() if a['name']=='scpi')['connection_parameters']
        for field in ('baudrate','parity','bytesize','stopbits','xonxoff','rtscts','dsrdtr'):
            self.assertIn(field, params['serial'])

    def test_run_context_preserves_original_exception(self):
        run = self.client.start_experiment()
        with self.assertRaisesRegex(RuntimeError, 'analysis failed'):
            with run:
                raise RuntimeError('analysis failed')
        self.assertEqual(run.wait(3)['state'], 'cancelled')

    def test_cli_batch_and_acquisition_share_the_same_experiment(self):
        path = self.engine.home / 'steps.json'
        path.write_text(json.dumps([self.step('a'), self.step('b')]))
        def call(*args):
            return json.loads(subprocess.check_output([sys.executable, '-m', 'ai4instruments.iop',
                '--endpoint', self.client.endpoint, *args], env=dict(os.environ, IOP_TOKEN=self.config['token']), text=True))
        run = self.client.start_experiment(resources=['stage'])
        records = call('batch', run.id, str(path), '--request-id', 'cli-batch', '--wait')
        saved = call('acquisition', run.id, 'read.json', records[-1]['id'], '--conditions', '{"sample":"A"}')
        self.assertEqual(saved['operation_ids'], [records[-1]['id']])
        self.assertEqual(call('finish', run.id)['state'], 'completed')
        self.assertEqual(call('release', 'stage')['state'], 'released')
        self.assertEqual(call('reconnect', 'stage')['state'], 'connected')

    def test_released_instrument_cannot_be_reserved_or_resumed_until_reconnected(self):
        run = self.client.start_experiment(resources=['stage'])
        run.invoke('stage','position'); run.cancel(); run.wait(3)
        self.client.release('stage')
        with self.assertRaises(IOPError):
            self.client.start_experiment(resources=['stage'])
        with self.assertRaises(IOPError):
            run.resume('resume-after-release')
        self.assertNotIn(run.id, self.engine.runs)
        self.client.reconnect('stage')
        run.resume('resume-after-release')
        run.invoke('stage','position'); run.finish()

    def test_discovery_does_not_rebind_a_released_instrument_to_another_address(self):
        first, row1 = self.instrument()
        second, row2 = self.instrument()
        device = self.scan([row1])['instruments'][0]['device_id']
        self.client.release(device)
        result = self.scan([row2])
        self.assertEqual(self.engine.device_records[device]['config']['port'], first.server_address[1])
        self.assertEqual(next(r for r in result['instruments'] if r['address']==row2['address'])['status'], 'released')
        self.assertIn(device, self.engine.released)

    def test_failed_connection_release_is_not_reported_as_ready(self):
        with patch.object(self.engine.devices['stage'], 'close', side_effect=RuntimeError('SDK did not close')):
            with self.assertRaises(IOPError):
                self.client.release('stage')
        self.assertEqual(self.client.request('/v1/devices/stage')['status']['state'], 'offline')
        self.client.reconnect('stage')
        self.assertEqual(self.client.request('/v1/devices/stage')['status']['state'], 'ready')
