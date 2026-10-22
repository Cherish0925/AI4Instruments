import json
import tempfile
import time
import unittest
from pathlib import Path
from . import test_service as fixture
from ai4instruments.iop import IOPError
from ai4instruments.iop.config import initialize
from ai4instruments.iop.engine import Engine


class PlatformCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    submit = fixture.ServiceCase.submit
    step = fixture.ServiceCase.step
    wait_running = fixture.ServiceCase.wait_running
    # The shared fixture supplies a live HTTP service and three simulated devices.
    def definition(self, id='bench', devices=None):
        return {'schema_version':1,'id':id,'devices':devices or ['stage','meter'],
                'resources':[{'id':'sample-a','devices':devices or ['stage','meter']}],
                'connections':[{'from':{'device':'stage','port':'sample'},'to':{'device':'meter','port':'input'},'kind':'measurement'}],
                'procedures':{'initialize':{'steps':[{'id':'position','device':'stage','operation':'move_to','arguments':{'angle_deg':0}}]}}}

    def test_configuration_revision_snapshot_and_initialization(self):
        spec=self.definition()
        p=self.client.configure_platform(spec)
        self.assertEqual(p['revision'],1)
        init=self.client.procedure('bench');init.result(5)
        self.assertEqual(init.info()['platform']['revision'],1)
        updated=dict(spec,name='New name')
        self.assertEqual(self.client.configure_platform(updated,1)['revision'],2)
        self.assertEqual(init.info()['platform']['definition']['name'],'bench')
        self.assertEqual([v['revision'] for v in self.client.request('/v1/platforms/bench/history')],[2,1])
        with self.assertRaises(IOPError):self.client.configure_platform(updated,1)

    def test_shared_resource_applies_across_platform_and_unscoped_calls(self):
        self.client.configure_platform(self.definition())
        self.client.configure_platform({'schema_version':1,'id':'other','devices':['aux'],
            'resources':[{'id':'sample-a','devices':['aux']}]})
        a=self.submit([self.step('a','stage',0.2)],platform='bench')
        self.wait_running(a)
        b=self.submit([self.step('b','aux',0.02)],platform='other')
        c=self.submit([self.step('c','meter',0.02)])
        for run in (a,b,c):run.result(5)
        ops=sorted([r.info()['operation_records'][0] for r in (a,b,c)],key=lambda x:x['started'])
        for left,right in zip(ops,ops[1:]):self.assertLessEqual(left['ended'],right['started'])

    def test_independent_platforms_continue_concurrently(self):
        self.client.configure_platform(self.definition())
        self.client.configure_platform({'schema_version':1,'id':'other','devices':['aux']})
        a=self.submit([self.step('a','stage',0.3)],platform='bench')
        b=self.submit([self.step('b','aux',0.3)],platform='other')
        a.result(5);b.result(5)
        left,right=(r.info()['operation_records'][0] for r in (a,b))
        self.assertLess(left['started'],right['ended']);self.assertLess(right['started'],left['ended'])

    def test_operation_selection_allows_independent_configuration(self):
        spec=self.definition()
        spec['resources'][0]['operations']={'stage':['move_to'],'meter':['measure']}
        self.client.configure_platform(spec)
        a=self.submit([self.step('a','stage',0.2)],platform='bench')
        b=self.submit([self.step('b','meter',0.2)],platform='bench')
        a.result(5);b.result(5)
        left,right=(r.info()['operation_records'][0] for r in (a,b))
        self.assertLess(left['started'],right['ended'])
        self.assertLess(right['started'],left['ended'])

    def test_active_work_keeps_its_platform_configuration(self):
        spec=self.definition();self.client.configure_platform(spec)
        run=self.submit([self.step('a','stage',0.3)],platform='bench');self.wait_running(run)
        with self.assertRaises(IOPError):self.client.configure_platform(dict(spec,name='changed'),1)
        self.assertEqual(self.client.platform('bench')['revision'],1);run.result(5)
        self.assertEqual(self.client.configure_platform(dict(spec,name='changed'),1)['revision'],2)

    def test_preview_rejects_missing_devices_and_cycles_without_writing(self):
        spec=self.definition();spec['devices']=['missing']
        with self.assertRaises(IOPError):self.client.request('/v1/platforms/preview',{'definition':spec})
        spec=self.definition();spec['procedures']['initialize']['steps'][0]['after']=['position']
        with self.assertRaises(IOPError):self.client.configure_platform(spec)
        self.assertEqual(self.client.platforms(),[])

    def test_platform_membership_for_workflow_and_program(self):
        self.client.configure_platform(self.definition())
        with self.assertRaises(IOPError):self.submit([self.step('a','aux',0)],platform='bench')
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'experiment.py').write_text("from ai4instruments.iop import Client\nClient().current_run().invoke('aux','position')\n")
            run=self.client.submit_package(directory,platform='bench')
            self.assertEqual(run.wait(6)['state'],'failed')


class PlatformPersistenceCase(unittest.TestCase):
    def test_saved_platform_and_shared_resources_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            config=initialize(directory,True,0);config['discovery_interval']=0
            first=Engine(directory,config)
            first.apply_platform({'schema_version':1,'id':'bench','devices':['stage','meter'],
                                  'resources':[{'id':'sample-a','devices':['stage','meter']}]})
            first.close()
            second=Engine(directory,config)
            self.assertEqual(second.platform_info('bench')['revision'],1)
            self.assertIn('shared:sample-a',second._resources(['stage']))
            second.close()
