import json
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import CancelledError
from pathlib import Path
from ai4instruments.iop import Driver, IOPError
from ai4instruments.iop.jobs import NativeJob
from . import test_service as fixture
from .test_process_driver import available


class ParallelDriver(Driver):
    def __init__(self, *args):
        super().__init__(*args)
        self.lock = threading.Lock()
        self.active = self.maximum = self.calls = 0

    def describe(self):
        return {'mode':'software', 'concurrency':8, 'requirements':self.config.get('requirements', {}),
                'operations':{'calculate':{'parameters':{'x':{'type':'number','default':1},
                              'duration':{'type':'number','default':0.15}}}}}

    def invoke(self, operation, arguments, cancelled):
        with self.lock:
            self.active += 1
            self.calls += 1
            self.maximum = max(self.maximum, self.active)
        try:
            cancelled.progress(0.5, 'Computing')
            if cancelled.wait(arguments['duration']):
                raise CancelledError()
            return {'value':arguments['x'] * 2}
        finally:
            with self.lock:
                self.active -= 1


class ExecutionCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    wait_running = fixture.ServiceCase.wait_running

    def register(self, requirements=None):
        self.client.register({'id':'calculator', 'driver':__name__ + ':ParallelDriver',
                              'config':{'requirements':requirements or {}}})

    def step(self, name, **fields):
        return {'id':name,'device':'calculator','operation':'calculate',**fields}

    def test_capacity_limits_parallel_work_across_experiments(self):
        self.client.configure_resources({'cpu':4,'solver':2})
        self.register({'cpu':2,'solver':1})
        runs = [self.client.submit([self.step(str(i))]) for i in range(10)]
        for run in runs:
            self.assertEqual(run.result(8)[run.info()['operation_records'][0]['step']]['value'], 2)
        self.assertEqual(self.engine.devices['calculator'].maximum, 2)
        self.assertTrue(all(row['used'] == 0 for row in self.client.resources()['allocation']))

    def test_reservation_is_counted_once_and_capacity_can_change_after_completion(self):
        self.client.configure_resources({'cpu':4})
        self.register({'cpu':2})
        run = self.client.submit([self.step('a'),self.step('b')], requirements={'cpu':4})
        self.wait_running(run)
        with self.assertRaises(IOPError):
            self.client.configure_resources({'cpu':1})
        used = {row['resource']:row['used'] for row in self.client.resources()['allocation']}
        self.assertEqual(used['pool:cpu'],4)
        run.result(5)
        self.assertEqual(self.engine.devices['calculator'].maximum,2)
        self.client.configure_resources({'cpu':2})
        self.assertEqual(self.client.resources()['capacities'], {'cpu':2})

    def test_results_supply_typed_arguments_and_implied_dependencies(self):
        self.register()
        run = self.client.submit([self.step('first',arguments={'x':3,'duration':0}),
            self.step('second',arguments={'duration':0},bindings={'x':{'step':'first','path':['value']}})])
        self.assertEqual(run.result(5)['second']['value'],12)
        self.assertEqual(run.info()['operation_records'][1]['arguments']['x'],6)
        with self.assertRaises(IOPError):
            self.client.submit([self.step('a',bindings={'x':{'step':'b'}}), self.step('b',after=['a'])])

    def test_missing_result_field_fails_before_calling_dependent_driver(self):
        self.register()
        run = self.client.submit([self.step('a',arguments={'duration':0}),
            self.step('b',bindings={'x':{'step':'a','path':['missing']}})])
        self.assertEqual(run.wait(5)['state'],'failed')
        self.assertEqual(self.engine.devices['calculator'].calls,1)
        self.assertTrue(all(row['used'] == 0 for row in self.client.resources()['allocation']))

    def test_long_poll_returns_progress_and_reconnection_does_not_replace_active_driver(self):
        self.register()
        run = self.client.submit([self.step('a',arguments={'duration':0.4})])
        self.wait_running(run)
        with self.assertRaises(IOPError):
            self.client.reconnect('calculator')
        events = list(run.watch())
        self.assertTrue(any(event['kind'] == 'operation.progress' for event in events))
        self.assertTrue(any(event['kind'] == 'run.completed' for event in events))
        self.assertEqual(self.client.reconnect('calculator')['state'],'connected')

    def test_binary_upload_download_and_file_index(self):
        self.register()
        run = self.client.submit([self.step('a',arguments={'duration':0})])
        run.result(5)
        file = Path(self.temp.name) / 'measurements.bin'
        data = bytes(range(256)) * 8193
        file.write_bytes(data)
        record = run.upload(file, 'arrays/measurements.bin')
        self.assertEqual(record['size'],len(data))
        self.assertEqual(self.client.request('/v1/artifacts/' + record['id'],binary=True),data)
        self.assertEqual(len(list((Path(self.temp.name) / 'incoming').iterdir())),0)

    def test_long_running_package_archives_completed_calls_and_pages_history(self):
        program = Path(self.temp.name) / 'long-program'
        program.mkdir()
        (program / 'experiment.py').write_text('''import os,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from ai4instruments.iop import Client
run=Client().current_run()
with ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(lambda i:run.invoke('stage','position',request_id='call-'+str(i)),range(120)))
run.save_result({'count':120})
while not Path(os.environ['IOP_RUN_DIR'],'finish').exists(): time.sleep(0.02)
''')
        run = self.client.submit_package(program, resources=['stage'])
        deadline = time.monotonic()+15
        while self.engine.store.get('runs',run.id).get('result') != {'count':120} and time.monotonic()<deadline:
            time.sleep(0.02)
        self.assertEqual(self.engine.store.get('runs',run.id)['result'],{'count':120})
        with self.engine.lock:
            self.assertEqual(self.engine.runs[run.id]['operations'],[])
            self.assertFalse(self.engine.operations)
        records=[]; cursor=0
        while True:
            page=run.operations(cursor,31)
            if not page['operations']: break
            records.extend(page['operations']);cursor=page['cursor']
        self.assertEqual(len({record['id'] for record in records}),120)
        self.assertTrue(all(record['state']=='completed' for record in records))
        (Path(self.temp.name)/'runs'/run.id/'output'/'finish').touch()
        self.assertEqual(run.result(5)['count'],120)
        self.assertEqual(run.info()['operation_count'],120)

    def test_software_discovery_uses_configured_executable_names(self):
        from ai4instruments.iop.discovery import discover
        result = discover([{'id':'python','executables':[sys.executable]}])
        self.assertTrue(any(item.get('program') == 'python' and Path(item['address']).is_file() for item in result['connections']))
        self.assertIn('command', [entry['name'] for entry in self.client.adapters()])


@unittest.skipUnless(available, 'Build iop-execd to run program execution cases')
class ProgramCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def test_command_program_produces_result_progress_and_files(self):
        script = Path(self.temp.name) / 'program.py'
        script.write_text('''import json,sys,time,os
from pathlib import Path
request=json.load(sys.stdin)
Path(os.environ['IOP_PROGRESS_FILE']).write_text(json.dumps({'fraction':0.5,'message':'Working'}))
time.sleep(0.3)
Path(os.environ['IOP_OUTPUT_DIR'],'samples.csv').write_text('x,y\\n1,2\\n')
Path(os.environ['IOP_RESULT_FILE']).write_text(json.dumps({'answer':request['arguments']['x']*3}))
''')
        self.client.register({'id':'program','driver':'command','config':{'concurrency':4,'operations':{
            'calculate':{'command':['{python}',str(script)],'parameters':{'x':{'type':'number'}}}}}})
        run = self.client.submit([{'id':'a','device':'program','operation':'calculate','arguments':{'x':7}}])
        self.assertEqual(run.result(8)['a']['answer'],21)
        self.assertTrue(any(f['name'].endswith('samples.csv') for f in run.files()))
        self.assertTrue(any(e['kind']=='operation.progress' for e in self.client.events(run_id=run.id)['events']))

    def test_native_completion_cancellation_and_parent_disconnect_end_descendants(self):
        for action in ('complete','cancel','disconnect'):
            with self.subTest(action=action):
                folder = Path(self.temp.name) / action; folder.mkdir()
                sentinel = folder / 'child-survived'
                child_code = 'import time; from pathlib import Path; time.sleep(1); Path(' + repr(str(sentinel)) + ').write_text("alive")'
                program = folder / 'parent.py'
                program.write_text('import subprocess,sys,time\nfrom pathlib import Path\n'
                    'subprocess.Popen([sys.executable,"-c",' + repr(child_code) + '])\n'
                    'Path("started").write_text("yes")\n' + ('time.sleep(10)\n' if action != 'complete' else ''))
                job = NativeJob([sys.executable,str(program)],folder,{},folder/'out',folder/'err')
                deadline = time.monotonic()+5
                while not (folder/'started').exists() and time.monotonic()<deadline:
                    time.sleep(0.01)
                self.assertTrue((folder/'started').is_file())
                if action == 'cancel': job.terminate()
                if action == 'disconnect': job.close()
                else:
                    self.assertTrue(job.done.wait(5))
                    self.assertEqual(job.returncode,0 if action=='complete' else -1)
                    job.close()
                time.sleep(1.1)
                self.assertFalse(sentinel.exists())

    def test_operation_progress_crosses_native_worker_protocol(self):
        worker = Path(self.temp.name) / 'reporting.py'
        worker.write_text('''import json,sys,time
for line in sys.stdin:
    m=json.loads(line)
    if m['method']=='configure': result={}
    elif m['method']=='describe': result={'operations':{'calculate':{'parameters':{'x':{'type':'number'},'duration':{'type':'number'}}}}}
    else:
        print(json.dumps({'id':m['id'],'event':'progress','progress':{'fraction':0.5,'message':'Working'}}),flush=True)
        time.sleep(m['params']['arguments']['duration'])
        result={'value':m['params']['arguments']['x']*2}
    print(json.dumps({'id':m['id'],'result':result}),flush=True)
''')
        self.client.register({'id':'reported','driver':'process','config':{'command':['{python}',str(worker)]}})
        run = self.client.submit([{'id':'a','device':'reported','operation':'calculate','arguments':{'x':4,'duration':0.3}}])
        self.assertEqual(run.result(8)['a']['value'],8)
        self.assertTrue(any(e['kind']=='operation.progress' for e in self.client.events(run_id=run.id)['events']))


class RemoteCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    wait_running = fixture.ServiceCase.wait_running

    def test_async_http_adapter_connects_another_runtime_and_waits_for_cancellation(self):
        from ai4instruments.iop.config import initialize
        from ai4instruments.iop.engine import Engine
        from ai4instruments.iop.server import Server
        with tempfile.TemporaryDirectory() as home:
            config = initialize(home, True, 0); config['discovery_interval'] = 0
            engine = Engine(home, config); server = Server(('127.0.0.1',0),engine)
            engine.start(); threading.Thread(target=server.serve_forever,daemon=True).start()
            try:
                self.client.register({'id':'remote','driver':'http','config':{
                    'base_url':engine.endpoint,'headers':{'Authorization':'Bearer '+config['token']},'operations':{
                        'wait':{'parameters':{'duration':{'type':'number'}},'method':'POST','path':'/v1/runs',
                            'body':{'steps':[{'id':'wait','device':'stage','operation':'wait','arguments':{'duration':'${duration}'}}]},
                            'job':{'status':{'path':'/v1/runs/{job_id}'},'poll_interval':0.02,
                                   'cancel':{'method':'POST','path':'/v1/runs/{job_id}/cancel','body':{}}}}}}})
                finished = self.client.submit([{'id':'remote','device':'remote','operation':'wait','arguments':{'duration':0.05}}])
                self.assertEqual(finished.result(5)['remote']['value']['wait']['elapsed_s'],0.05)
                run = self.client.submit([{'id':'remote','device':'remote','operation':'wait','arguments':{'duration':4}}])
                self.wait_running(run)
                deadline = time.monotonic()+3
                while not engine.runs and time.monotonic()<deadline: time.sleep(0.01)
                run.cancel()
                self.assertEqual(run.wait(5)['state'],'cancelled')
                self.assertEqual(engine.store.list('runs')[0]['state'],'cancelled')
                self.assertFalse(self.engine.resource_holds)
            finally:
                server.shutdown();server.server_close();engine.close()


class MigrationCase(unittest.TestCase):
    def test_previous_artifact_records_gain_name_index_without_losing_content(self):
        import sqlite3
        from ai4instruments.iop.store import Store
        with tempfile.TemporaryDirectory() as home:
            path = Path(home) / 'records.sqlite3'
            db = sqlite3.connect(path)
            db.execute('CREATE TABLE artifacts(id TEXT PRIMARY KEY, run_id TEXT NOT NULL, body TEXT NOT NULL)')
            record = {'id':'file-old','run_id':'run-old','name':'output/data.csv','size':12}
            db.execute('INSERT INTO artifacts VALUES(?,?,?)', ('file-old','run-old',json.dumps(record)))
            db.commit();db.close()
            store = Store(path)
            try:
                self.assertEqual(store.artifact_named('run-old','output/data.csv'),record)
            finally: store.close()

