import io
import json
import socketserver
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path
from ai4instruments.iop import Client, Driver, IOPError
from ai4instruments.iop.config import initialize, InstanceLock
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server
from ai4instruments.iop.store import Store


class SlowDriver(Driver):
    """Completes an in-flight action before releasing its resource."""
    def describe(self):
        return {'operations':{'work':{'parameters':{}}}}
    def invoke(self, operation, arguments, cancelled):
        time.sleep(0.2)
        return {'done':True}


class ServiceCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = initialize(self.temp.name, True, 0)
        # These cases exercise simulated instruments. Discovery has its own
        # tests and must not enumerate the host's USB devices for every case.
        self.config['discovery_interval'] = 0
        self.engine = Engine(self.temp.name, self.config)
        self.server = Server(('127.0.0.1',0), self.engine)
        self.engine.start()
        self.http = threading.Thread(target=self.server.serve_forever, daemon=True); self.http.start()
        self.client = Client(self.engine.endpoint, token=self.config['token'])

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.engine.close(); self.temp.cleanup()

    def submit(self, steps, **kwargs):
        return self.client.submit(steps, **kwargs)

    def step(self, name, device='stage', duration=0.1, after=()):
        return {'id':name,'device':device,'operation':'wait','arguments':{'duration':duration},'after':list(after)}

    def events(self, run):
        return self.client.events(run_id=run.id)['events']

    def wait_running(self, run):
        deadline=time.monotonic()+3
        while time.monotonic()<deadline:
            if any(o['state']=='running' for o in run.info()['operation_records']):return
            time.sleep(0.01)
        self.fail('Operation did not start')

    def test_parallel_devices_and_dependency_join(self):
        run=self.submit([self.step('a','stage',0.15),self.step('b','aux',0.15),self.step('c','meter',0,('a','b'))])
        result=run.result(5);self.assertEqual(set(result),{'a','b','c'})
        ops={o['step']:o for o in run.info()['operation_records']}
        self.assertLess(ops['a']['started'],ops['b']['ended']);self.assertLess(ops['b']['started'],ops['a']['ended'])
        self.assertGreaterEqual(ops['c']['started'],max(ops['a']['ended'],ops['b']['ended']))

    def test_same_device_serializes_across_runs(self):
        runs=[self.submit([self.step(str(i),duration=0.03)]) for i in range(8)]
        for r in runs:r.result(6)
        ops=sorted([r.info()['operation_records'][0] for r in runs],key=lambda o:o['started'])
        for a,b in zip(ops,ops[1:]):self.assertLessEqual(a['ended'],b['started'])

    def test_experiment_reservation_survives_between_steps(self):
        first=self.submit([self.step('a','stage',0.08),self.step('b','meter',0.12,('a',)),self.step('c','stage',0.03,('b',))],resources=['stage','meter'])
        self.wait_running(first)
        second=self.submit([self.step('x','stage',0.01)])
        first.result(5);second.result(5)
        self.assertGreaterEqual(second.info()['operation_records'][0]['started'],first.info()['operation_records'][-1]['ended'])

    def test_overlapping_reservations_do_not_deadlock(self):
        runs=[self.submit([self.step('a','stage',0.03),self.step('b','meter',0.03,('a',))],resources=['meter','stage']) for _ in range(5)]
        for r in runs:r.result(8)
        self.assertFalse(self.engine.metrics()['errors'])

    def test_cancel_retains_resource_until_driver_finishes(self):
        self.client.register({'id':'slow','driver':__name__+':SlowDriver'})
        first=self.submit([{'id':'a','device':'slow','operation':'work'}])
        self.wait_running(first);first.cancel()
        second=self.submit([{'id':'b','device':'slow','operation':'work'}])
        self.assertEqual(first.wait(5)['state'],'cancelled');second.result(5)
        self.assertLessEqual(first.info()['operation_records'][0]['ended'],second.info()['operation_records'][0]['started'])

    def test_failure_keeps_results_and_stops_dependents(self):
        self.client.register({'id':'broken','driver':'scpi','config':{'host':'127.0.0.1','port':1,'timeout':0.1}})
        run=self.submit([{'id':'a','device':'broken','operation':'identify'},self.step('b','stage',0,('a',))])
        self.assertEqual(run.wait(4)['state'],'failed')
        self.assertEqual([o['state'] for o in run.info()['operation_records']],['failed','cancelled'])

    def test_bad_dependency_and_argument_do_not_create_work(self):
        for steps in [[self.step('a',after=('missing',))],[{'id':'a','device':'stage','operation':'move_to','arguments':{'angle_deg':'bad'}}]]:
            with self.assertRaises(IOPError):self.submit(steps)
        self.assertEqual(self.client.request('/v1/runs'),[])

    def test_submission_retry_keeps_one_run(self):
        a=self.submit([self.step('a',duration=0)],request_id='same')
        b=self.submit([self.step('a',duration=0)],request_id='same')
        self.assertEqual(a.id,b.id);a.result(5)
        with self.assertRaises(IOPError):self.submit([self.step('a',duration=0.1)],request_id='same')

    def test_real_package_uses_service_and_persists_outputs(self):
        root=Path(__file__).resolve().parents[2]/'examples/iop/polarization'
        run=self.client.submit_package(root, resources=['stage','meter'], parameters={'angles_deg':[0,15,45]})
        self.assertEqual(run.result(12)['points'],3)
        names=[f['name'] for f in run.files()]
        self.assertIn('output/scan.csv',names);self.assertIn('stdout.txt',names);self.assertIn('package.zip',names)
        self.assertTrue(all(o['state']=='completed' for o in run.info()['operation_records']))
        artifact=next(f for f in run.files() if f['name']=='output/scan.csv')
        self.assertIn(b'angle_deg,power_W,time',self.client.request('/v1/artifacts/'+artifact['id'],binary=True))

    def test_package_cannot_extend_a_partial_reservation(self):
        code="from ai4instruments.iop import Client\nClient().current_run().invoke('meter','measure')\n"
        with tempfile.TemporaryDirectory() as folder:
            Path(folder,'experiment.py').write_text(code)
            run=self.client.submit_package(folder, resources=['stage'])
            self.assertEqual(run.wait(6)['state'],'failed')

    def test_package_paths_remain_inside_run(self):
        import base64
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:z.writestr('../outside.py','bad')
        with self.assertRaises(IOPError):self.client.request('/v1/packages',{'archive':base64.b64encode(buf.getvalue()).decode()})
        self.assertFalse(Path(self.temp.name,'outside.py').exists())

    def test_http_requires_the_platform_token(self):
        with self.assertRaises(IOPError):Client(self.engine.endpoint,token='wrong').devices()

    def test_one_service_owns_the_data_directory(self):
        a=InstanceLock(self.temp.name)
        try:
            with self.assertRaises(RuntimeError):InstanceLock(self.temp.name)
        finally:a.close()
        b=InstanceLock(self.temp.name);b.close()


class PersistenceCase(unittest.TestCase):
    def test_restart_retains_queued_and_interrupts_started_work(self):
        with tempfile.TemporaryDirectory() as home:
            config=initialize(home,True,0)
            first=Engine(home,config)
            queued=first.submit({'steps':[{'id':'a','device':'stage','operation':'position'}]})
            started=first.submit({'steps':[{'id':'b','device':'aux','operation':'position'}]})
            r=first.runs[started['id']];r['state']='running'
            op=first.operations[r['operations'][0]];op['state']='running'
            with first.store.transaction():first.store.put('runs',r);first.store.put('operations',op)
            first.store.close();first.pool.shutdown()
            second=Engine(home,config)
            self.assertEqual(second.store.get('runs',started['id'])['state'],'interrupted')
            self.assertEqual(second.store.get('operations',op['id'])['state'],'interrupted')
            self.assertEqual(second.store.get('runs',queued['id'])['state'],'queued')
            second.start()
            limit=time.monotonic()+3
            while second.store.get('runs',queued['id'])['state']!='completed' and time.monotonic()<limit:time.sleep(0.02)
            self.assertEqual(second.store.get('runs',queued['id'])['state'],'completed');second.close()


class SCPICase(unittest.TestCase):
    def test_tcp_driver_uses_a_real_socket_and_reads_completion(self):
        from ai4instruments.iop.drivers import SCPI
        commands=[]
        class Instrument(socketserver.StreamRequestHandler):
            def handle(self):
                while True:
                    line=self.rfile.readline()
                    if not line:return
                    command=line.decode().strip();commands.append(command)
                    if command=='*IDN?':self.wfile.write(b'Maker,Model,Serial,1\n')
                    elif command=='*OPC?':self.wfile.write(b'1\n')
                    elif command=='MEAS:POW?':self.wfile.write(b'0.125\n')
        server=socketserver.ThreadingTCPServer(('127.0.0.1',0),Instrument);server.daemon_threads=True
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        driver=SCPI('meter',{'host':'127.0.0.1','port':server.server_address[1],'operations':{
            'power':{'parameters':{},'query':'MEAS:POW?','result':{'type':'number','unit':'W'}},
            'setup':{'parameters':{},'write':'CONF:POW','completion':{'query':'*OPC?'}}}}, {})
        try:
            self.assertEqual(driver.invoke('identify',{},threading.Event())['value'],'Maker,Model,Serial,1')
            self.assertEqual(driver.invoke('setup',{},threading.Event())['completion_response'],'1')
            self.assertEqual(driver.invoke('power',{},threading.Event())['value'],0.125)
            self.assertEqual(commands,['*IDN?','CONF:POW','*OPC?','MEAS:POW?'])
        finally:driver.close();server.shutdown();server.server_close()


class DiscoveryCase(unittest.TestCase):
    def test_profiles_match_the_connection_and_fill_the_address(self):
        from ai4instruments.iop.discovery import match_profiles
        inventory={'connections':[{'transport':'serial','vid':123,'pid':456,'address':'COM4','serial_number':'AB'}]}
        profiles=[{'match':{'transport':'serial','vid':123,'pid':456},'device':{
            'id':'meter-{serial_number}','driver':'scpi','config':{'transport':'serial','port':'{address}'}}}]
        self.assertEqual(match_profiles(inventory,profiles)[0]['config']['port'],'COM4')
        profiles[0]['match']['pid']=999
        self.assertEqual(match_profiles(inventory,profiles),[])

    def test_native_startup_uses_exact_argument_paths(self):
        from ai4instruments.iop.services import systemd_unit, launchd_plist, windows_script
        import plistlib
        self.assertIn('"/home/user/a b"',systemd_unit('/usr/bin/python','/home/user/a b'))
        self.assertEqual(plistlib.loads(launchd_plist('/path/python','/a b'))['ProgramArguments'][-2:],['/a b','serve'])
        script=windows_script('C:\\A B\\python.exe','C:\\User Data\\IOP')
        self.assertIn("'C:\\A B\\python.exe'",script)
        self.assertIn('C:\\User Data\\IOP',script)


if __name__=='__main__':unittest.main()
