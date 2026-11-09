"""External programs retain one experiment across calls and client connections."""
import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from ai4instruments.iop import Client, IOPError
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server
from . import test_service as fixture
import unittest


class ExternalCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown
    wait_running = fixture.ServiceCase.wait_running

    def test_one_run_owns_operations_files_results_and_configuration(self):
        run = self.client.start_experiment(name='Scan', resources=['stage'])
        records = [run.invoke_record('stage', 'move_to', {'angle_deg':i}, request_id=f'{run.id}-{i}')
                   for i in range(3)]
        run.checkpoint({'next':3})
        file = run.save_file('scan.json', json.dumps([r['result'] for r in records]),
                             operation_ids=[r['id'] for r in records])
        source = Path(self.temp.name) / 'raw.bin'
        source.write_bytes(b'raw measurements')
        uploaded = run.upload(source, operation_ids=[records[-1]['id']])
        run.save_result({'points':3})
        self.assertEqual(run.finish()['state'], 'completed')
        self.assertEqual(run.finish()['state'], 'completed')
        self.assertEqual(run.result(3), {'points':3})
        self.assertEqual(len(self.client.request('/v1/runs')), 1)
        self.assertEqual(run.info()['operation_count'], 3)
        self.assertEqual({r['run_id'] for r in records}, {run.id})
        self.assertEqual({r['device_revision'] for r in records},
                         {run.info()['devices']['stage']['revision']})
        files = {f['id']: f for f in run.files()}
        self.assertEqual(files[file['id']]['operation_ids'], [r['id'] for r in records])
        self.assertEqual(files[uploaded['id']]['operation_ids'], [records[-1]['id']])
        self.assertEqual(self.client.request('/v1/artifacts/'+uploaded['id'], binary=True), source.read_bytes())
        self.assertNotIn(run.id, self.engine.runs)
        self.assertEqual(self.engine.metrics()['errors'], [])

    def test_new_client_reuses_run_and_operation_even_after_finish(self):
        run = self.client.start_experiment(request_id='scan')
        first = run.invoke_record('stage', 'move_to', {'angle_deg':7}, request_id='move-7')
        client = Client(self.engine.endpoint, token=self.config['token'])
        rejoined = client.start_experiment(request_id='scan')
        self.assertEqual(rejoined.id, run.id)
        self.assertEqual(rejoined.invoke_record('stage', 'move_to', {'angle_deg':7}, request_id='move-7')['id'], first['id'])
        rejoined.finish()
        self.assertEqual(rejoined.invoke_record('stage', 'move_to', {'angle_deg':7}, request_id='move-7')['id'], first['id'])
        self.assertEqual(len(run.operations()['operations']), 1)
        with self.assertRaises(IOPError):
            rejoined.invoke('stage', 'move_to', {'angle_deg':8}, request_id='move-7')
        with self.assertRaises(IOPError):
            rejoined.invoke('stage', 'position')

    def test_reservation_survives_gaps_and_finishing_releases_it(self):
        run = self.client.start_experiment(resources=['stage'])
        run.invoke('stage', 'move_to', {'angle_deg':9})
        other = self.client.submit([{'id':'read','device':'stage','operation':'position'}])
        independent = self.client.submit([{'id':'read','device':'aux','operation':'position'}])
        independent.result(3)
        self.assertNotEqual(other.info(False)['state'], 'completed')
        self.assertEqual(run.info(False)['state'], 'running')
        run.finish()
        self.assertEqual(other.result(3)['read']['angle_actual'], 9)

    def test_calls_can_be_accepted_while_reservation_is_queued(self):
        holder = self.client.start_experiment(resources=['stage'])
        holder.invoke('stage', 'position')
        queued = self.client.start_experiment(resources=['stage'])
        op = self.client.request('/v1/runs/'+queued.id+'/operations',
                                 {'device':'stage','operation':'position','request_id':'queued-read'})
        self.assertEqual(queued.info(False)['state'], 'queued')
        with self.assertRaises(IOPError) as error:
            queued.finish()
        self.assertEqual(error.exception.code, 'operations_pending')
        holder.finish()
        finished = queued.invoke_record('stage', 'position', request_id='queued-read', timeout=3)
        self.assertEqual(finished['id'], op['id'])
        queued.finish()

    def test_cancel_keeps_record_and_stops_in_flight_work(self):
        run = self.client.start_experiment(resources=['stage'])
        self.client.request('/v1/runs/'+run.id+'/operations',
                            {'device':'stage','operation':'wait','arguments':{'duration':1}})
        self.wait_running(run)
        run.cancel()
        self.assertEqual(run.wait(3)['state'], 'cancelled')
        with self.assertRaises(IOPError):
            run.finish()
        self.assertEqual(len(run.operations()['operations']), 1)
        self.assertEqual(self.engine.metrics()['errors'], [])

    def test_failure_does_not_leave_an_external_experiment_running(self):
        self.client.register({'id':'broken','driver':'scpi','config':{'host':'127.0.0.1','port':1,'timeout':0.1}})
        run = self.client.start_experiment()
        with self.assertRaises(IOPError):
            run.invoke('broken', 'identify', timeout=3)
        self.assertEqual(run.wait(3)['state'], 'failed')

    def test_partial_reservation_and_foreign_file_links_are_rejected(self):
        run = self.client.start_experiment(resources=['stage'])
        with self.assertRaises(IOPError):
            run.invoke('meter', 'measure')
        other = self.client.start_experiment()
        op = other.invoke_record('aux', 'position')
        with self.assertRaises(IOPError):
            run.save_file('foreign.json', '{}', operation_ids=[op['id']])
        self.assertEqual(run.files(), [])
        other.finish(); run.finish()

    def test_external_restart_requires_explicit_resume_and_keeps_old_operations(self):
        run = self.client.start_experiment(resources=['stage'])
        first = run.invoke_record('stage', 'move_to', {'angle_deg':3}, request_id='first-point')
        run.checkpoint({'next':1})
        self.server.shutdown(); self.server.server_close(); self.engine.close()
        self.engine = Engine(self.temp.name, self.config)
        self.server = Server(('127.0.0.1', 0), self.engine)
        self.engine.start()
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.client.endpoint = self.engine.endpoint
        self.assertEqual(run.info()['state'], 'interrupted')
        self.assertTrue(run.info()['can_resume'])
        self.assertEqual(run.resume('resume-scan')['attempt'], 2)
        self.assertEqual(run.resume('resume-scan')['attempt'], 2)
        self.assertEqual(run.checkpoints()['main']['state'], {'next':1})
        self.assertEqual(run.invoke_record('stage', 'move_to', {'angle_deg':3}, request_id='first-point')['id'], first['id'])
        run.invoke('stage', 'move_to', {'angle_deg':4}, request_id='second-point')
        run.finish()
        self.assertEqual(len(run.operations()['operations']), 2)

    def test_empty_external_run_finishes_and_workflows_cannot_be_finished_by_client(self):
        run = self.client.start_experiment()
        run.save_result({'points':0})
        run.finish()
        self.assertEqual(run.result(3), {'points':0})
        workflow = self.client.submit([{'id':'read','device':'stage','operation':'position'}])
        workflow.result(3)
        with self.assertRaises(IOPError) as error:
            workflow.finish()
        self.assertEqual(error.exception.code, 'not_external')

    def test_long_experiment_keeps_only_pending_operations_in_memory(self):
        run = self.client.start_experiment()
        for i in range(30):
            run.invoke('stage', 'position', request_id=f'point-{i}')
        with self.engine.lock:
            self.assertEqual(self.engine.runs[run.id]['operations'], [])
            self.assertEqual(self.engine.operations, {})
        self.assertEqual(run.info(False)['operation_count'], 30)
        run.finish()

    def test_submission_request_id_cannot_switch_run_kind(self):
        run = self.client.start_experiment(request_id='one-submission')
        with self.assertRaises(IOPError):
            self.client.request('/v1/packages', {'kind':'external', 'request_id':'one-submission','archive':'AA=='})
        run.finish()

    def test_cli_invocations_share_one_external_experiment(self):
        env = dict(os.environ, IOP_TOKEN=self.config['token'])
        def call(*arguments):
            return json.loads(subprocess.check_output([sys.executable, '-m', 'ai4instruments.iop',
                '--endpoint', self.client.endpoint, *arguments], env=env, text=True))
        run_id = call('begin', '--request-id', 'cli-scan', '--resources', 'stage')['run_id']
        first = call('call', 'stage', 'position', '--run-id', run_id, '--request-id', 'cli-read')
        self.assertEqual(first['run_id'], run_id)
        self.assertEqual(call('call', 'stage', 'position', '--run-id', run_id, '--request-id', 'cli-read')['id'], first['id'])
        self.assertEqual(call('finish', run_id)['state'], 'completed')
        self.assertEqual(len(self.client.request('/v1/runs')), 1)

    def test_unknown_physical_outcome_is_not_replayed_on_continuation(self):
        run = self.client.start_experiment(resources=['stage'])
        op = run.invoke_record('stage', 'position', request_id='known-read')
        self.engine.store.hold_resources(['device:stage'], op['id'], 'Instrument outcome needs observation')
        self.engine.resource_holds = self.engine.store.resource_holds()
        run.cancel(); run.wait(3)
        with self.assertRaises(IOPError) as error:
            run.resume('continue-after-interruption')
        self.assertEqual(error.exception.code, 'device_outcome_unknown')
        self.assertEqual(len(run.operations()['operations']), 1)

    def test_external_experiment_does_not_block_an_unrelated_platform_configuration(self):
        run = self.client.start_experiment()
        run.invoke('stage', 'position')
        unrelated = {'schema_version':1, 'id':'other-bench', 'devices':['aux']}
        self.assertEqual(self.client.configure_platform(unrelated)['revision'], 1)
        affected = {'schema_version':1, 'id':'scan-bench', 'devices':['stage']}
        with self.assertRaises(IOPError):
            self.client.configure_platform(affected)
        run.finish()
        self.assertEqual(self.client.configure_platform(affected)['revision'], 1)
