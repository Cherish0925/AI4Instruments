"""Connection updates, concise context, configuration changes and durable program progress."""
import copy
import io
import json
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from ai4instruments.iop import Client, IOPError
from ai4instruments.iop.config import initialize
from ai4instruments.iop.discovery import discover
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server
from ai4instruments.iop.store import Store
from ai4instruments.iop import streams
from . import test_service as fixture
from .test_process_driver import available


class ContinuityCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    wait_running = fixture.ServiceCase.wait_running

    def test_compact_context_and_changes_do_not_repeat_results_or_connection_inventory(self):
        self.engine.discovery = {'connections': [{'transport':'serial','address':'COM1','metadata':'x'*30000}],
                                 'providers':[], 'instruments':[], 'summary':{'interfaces':1}}
        summary, full = self.client.context(), self.client.context(detail='full')
        self.assertLess(len(json.dumps(summary)), len(json.dumps(full)) / 3)
        self.assertNotIn('connections', summary['discovery'])
        self.assertNotIn('definition', summary['platforms'][0] if summary['platforms'] else {})
        run = self.client.submit([{'id':'read','device':'stage','operation':'position'}])
        run.result(5)
        changes = self.client.changes(summary['cursor'], limit=100)
        self.assertTrue(any(e['kind']=='run.completed' for e in changes['changes']))
        self.assertTrue(all('result' not in e for e in changes['changes']))
        self.assertEqual(self.client.changes(changes['cursor'])['changes'], [])
        state = self.client.request('/v1/devices/stage')['status']
        self.assertEqual(state['state'], 'ready')
        self.assertEqual(state['communication']['state'], 'completed')
        self.assertIsNone(state['present'])

    def test_large_laboratory_context_has_a_complete_device_continuation(self):
        self.client.register_many([{'id':f'unit-{i}', 'driver':'simulated'} for i in range(105)])
        context = self.client.context()
        self.assertEqual(len(context['devices']), 100)
        page = self.client.request(context['devices_page']['next'])
        self.assertEqual(page['total'], 108)
        self.assertIsNone(page['next'])
        self.assertEqual(len({d['id'] for d in context['devices'] + page['devices']}), 108)

    def test_invalid_arguments_include_the_required_fields(self):
        with self.assertRaises(IOPError) as error:
            self.client.invoke('stage', 'move_to', {})
        self.assertEqual(error.exception.code, 'invalid_arguments')
        self.assertEqual(error.exception.status, 400)
        self.assertEqual(error.exception.details['parameters']['angle_deg']['unit'], 'deg')

    def test_configuration_can_change_and_restore_without_restarting(self):
        current = self.client.device_history('stage')[0]
        changed = copy.deepcopy(current['definition'])
        changed['config']['name'] = 'Translation stage'
        saved = self.client.configure_device('stage', changed, current['revision'])
        self.assertEqual(saved['revision'], current['revision'] + 1)
        self.assertEqual(self.client.request('/v1/devices/stage')['name'], 'Translation stage')
        with self.assertRaises(IOPError) as error:
            self.client.configure_device('stage', current['definition'], current['revision'])
        self.assertEqual(error.exception.code, 'configuration_changed')
        self.client.configure_device('stage', current['definition'], saved['revision'])
        self.assertEqual(len(self.client.device_history('stage')), 3)
        self.assertEqual(self.client.reconnect('stage')['state'], 'connected')
        self.assertEqual(self.client.invoke('stage', 'position')['angle_actual'], 0)

    def test_configuration_waits_for_accepted_work_and_restores_driver_after_invalid_change(self):
        current = self.client.device_history('stage')[0]
        changed = copy.deepcopy(current['definition'])
        changed['config']['name'] = 'New name'
        run = self.client.submit([{'id':'wait','device':'stage','operation':'wait','arguments':{'duration':0.3}}])
        with self.assertRaises(IOPError) as error:
            self.client.configure_device('stage', changed, current['revision'])
        self.assertEqual(error.exception.code, 'device_busy')
        run.result(5)
        changed['driver'] = 'not-installed-sdk'
        with self.assertRaises(IOPError):
            self.client.configure_device('stage', changed, current['revision'])
        self.assertEqual(self.client.device_history('stage')[0], current)
        self.assertEqual(self.client.invoke('stage', 'position')['angle_actual'], 0)

    def program(self, source):
        folder = Path(self.temp.name) / 'program'
        folder.mkdir()
        (folder / 'package.json').write_text(json.dumps({'command':['{python}','experiment.py'], 'resume':True}))
        (folder / 'experiment.py').write_text(source)
        return self.client.submit_package(folder, resources=['stage'])

    def test_program_progress_survives_service_restart_and_does_not_repeat_completed_operations(self):
        run = self.program('''import os,sys
from pathlib import Path
from ai4instruments.iop import Client
run=Client().current_run()
progress=run.checkpoints().get('main',{}).get('state',{'next':0})
for i in range(progress['next'],3):
    run.invoke('stage','move_to',{'angle_deg':i},request_id=run.id+'-'+str(i))
    run.checkpoint({'next':i+1})
    if i==0: sys.exit(17)
run.save_result({'measurements':3})
''')
        self.assertEqual(run.wait(8)['state'], 'failed')
        self.assertEqual(run.checkpoints()['main']['state'], {'next':1})
        self.server.shutdown(); self.server.server_close(); self.engine.close()
        self.config = initialize(self.temp.name)
        self.engine = Engine(self.temp.name, self.config)
        self.server = Server(('127.0.0.1', 0), self.engine)
        self.engine.start()
        self.http = threading.Thread(target=self.server.serve_forever, daemon=True); self.http.start()
        self.client.endpoint = self.engine.endpoint
        accepted = run.resume('continue-1')
        self.assertEqual(accepted['attempt'], 2)
        self.assertEqual(run.resume('continue-1')['attempt'], 2)
        self.assertEqual(run.result(8), {'measurements':3})
        operations = run.operations()['operations']
        self.assertEqual(len(operations), 3)
        self.assertEqual([o['arguments']['angle_deg'] for o in operations], [0,1,2])
        self.assertEqual(run.checkpoints()['main']['state']['next'], 3)
        self.assertTrue(any(f['name']=='attempts/1/stderr.txt' for f in run.files()))

    def test_progress_cannot_be_saved_while_instrument_action_is_in_flight(self):
        run = self.program('''import time
from ai4instruments.iop import Client
run=Client().current_run()
run.checkpoint({'next':0})
run.invoke('stage','wait',{'duration':1})
''')
        self.wait_running(run)
        with self.assertRaises(IOPError) as error:
            run.checkpoint({'next':1})
        self.assertEqual(error.exception.code, 'operations_pending')
        run.cancel(); run.wait(5)

    def test_binary_chunks_are_ordered_idempotent_and_do_not_block_instrument_commands(self):
        run = self.client.submit([{'id':'read','device':'stage','operation':'position'}]); run.result(5)
        stream = run.stream('measurements', {'format':'float32-le','channels':[{'name':'voltage','unit':'V'}]})
        payload = b'\x00\x00\x80\x3f' * 100000
        first = stream.append(payload, 0)
        self.assertEqual(stream.append(payload, 0)['id'], first['id'])
        with self.assertRaises(IOPError) as error:
            stream.append(b'different', 0)
        self.assertEqual(error.exception.code, 'chunk_changed')
        with self.assertRaises(IOPError) as error:
            stream.append(payload, 2)
        self.assertEqual(error.exception.details['next_sequence'], 1)
        entered, release = threading.Event(), threading.Event()
        class SlowInput(io.BytesIO):
            def read(self, size=-1):
                entered.set()
                if not release.wait(5): raise TimeoutError('release data transfer')
                return super().read(size)
        with ThreadPoolExecutor(max_workers=1) as pool:
            job = pool.submit(streams.append, self.engine, run.id, 'measurements', 1, SlowInput(payload), len(payload))
            try:
                self.assertTrue(entered.wait(3))
                self.client.invoke('stage','position', timeout=3)
            finally:
                release.set()
            job.result(3)
        self.assertEqual(stream.info()['next_sequence'], 2)
        self.assertEqual(stream.info()['bytes'], 2 * len(payload))
        page = stream.chunks(limit=1)
        self.assertEqual(page['cursor'], 0)
        self.assertEqual(stream.chunks(after=page['cursor'])['chunks'][0]['sequence'], 1)
        self.assertEqual(self.client.request('/v1/artifacts/'+first['id'], binary=True), payload)
        self.assertEqual(len(list((self.engine.home/'runs'/run.id/'output'/'streams'/'measurements').glob('*.bin'))), 2)
        store = Store(self.engine.home/'records.sqlite3')
        try:
            self.assertEqual(store.db.execute('SELECT chunks,bytes FROM streams WHERE run_id=?',(run.id,)).fetchone(), (2, 2*len(payload)))
        finally: store.close()

    @unittest.skipUnless(available, 'Build iop-execd')
    def test_installed_python_driver_can_use_the_existing_process_supervisor(self):
        self.client.register({'id':'isolated','driver':'simulated','config':{'kind':'stage'},
                              'execution':{'mode':'process','timeout':5}})
        self.assertEqual(self.client.invoke('isolated','move_to',{'angle_deg':11})['angle_actual'], 11)
        self.assertEqual(self.client.reconnect('isolated')['state'], 'connected')


class IncrementalCase(unittest.TestCase):
    def test_fast_provider_is_published_before_slow_provider_finishes(self):
        published, release = threading.Event(), threading.Event()
        snapshots = []
        def slow():
            if not release.wait(5): raise TimeoutError('release VISA')
            return [], [{'name':'visa','available':True}]
        def update(value):
            snapshots.append(copy.deepcopy(value))
            if any(r['transport']=='serial' for r in value['connections']): published.set()
        with patch('ai4instruments.iop.discovery._serial', return_value=([{'transport':'serial','address':'COM42'}],[{'name':'serial','available':True}])), \
             patch('ai4instruments.iop.discovery._visa', side_effect=slow), \
             patch('ai4instruments.iop.discovery._usb', return_value=([],[{'name':'usb-inventory','available':True}])), \
             patch('ai4instruments.iop.discovery._network', return_value=([],[{'name':'lxi-network','available':True}])), \
             patch('ai4instruments.iop.discovery.importlib.util.find_spec', return_value=None), \
             patch('ai4instruments.iop.discovery.entry_points', return_value=[]):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(discover, [], update)
                try:
                    self.assertTrue(published.wait(3))
                    self.assertFalse(future.done())
                    self.assertIn('visa', snapshots[-1]['pending_providers'])
                finally: release.set()
                self.assertEqual(future.result(3)['summary']['interfaces'], 1)


class RestartOutcomeCase(unittest.TestCase):
    def test_uncertain_operation_retains_resources_but_allows_declared_observations(self):
        with tempfile.TemporaryDirectory() as home:
            config = initialize(home, True, 0); config['discovery_interval'] = 0
            first = Engine(home, config)
            run = first.submit({'steps':[{'id':'move','device':'stage','operation':'move_to','arguments':{'angle_deg':12}}]})
            active = first.runs[run['id']]; active['state'] = 'running'
            op = first.operations[active['operations'][0]]; op['state'] = 'running'
            with first.store.transaction():
                first.store.put('runs', active); first.store.put('operations', op)
            first.store.close(); first.pool.shutdown()
            second = Engine(home, config); second.start()
            try:
                self.assertIn('device:stage', second.resource_holds)
                self.assertTrue(second.store.get('operations', op['id'])['outcome_unknown'])
                read = second.submit({'steps':[{'id':'position','device':'stage','operation':'position'}]})
                deadline = time.monotonic() + 3
                while second.store.get('runs', read['id'])['state'] not in ('completed','interrupted','failed') and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertEqual(second.store.get('runs', read['id'])['state'], 'completed')
                self.assertIn('device:stage', second.resource_holds)
                second.resolve_resources(['device:stage'], 'Position returned 0 degrees')
                self.assertFalse(second.resource_holds)
            finally: second.close()
