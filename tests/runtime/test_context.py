"""First connection, configuration reuse and MCP communication with a running service."""
import importlib.util
import json
import os
import queue
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from . import test_service as fixture
from ai4instruments.iop import IOPError, desktop
from ai4instruments.iop.context import agent_configuration
from ai4instruments.iop.config import initialize, save_json
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.drivers import Simulated


class ContextCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def test_context_reuses_configuration_and_contains_no_connection_token(self):
        self.client.configure_platform({'schema_version': 1, 'id': 'bench', 'devices': ['stage', 'meter', 'aux']})
        with patch.object(self.engine, 'scan', side_effect=AssertionError('Cached context must not scan')):
            context = self.client.context()
        self.assertEqual(context['setup']['unassigned_devices'], [])
        self.assertEqual(context['platforms'][0]['revision'], 1)
        self.assertEqual(context['devices'][0]['operations'], list(self.engine.descriptions['stage']['operations']))
        self.assertNotIn(self.config['token'], json.dumps(context))
        self.assertFalse(context['operation']['configuration_executes_actions'])
        self.assertEqual(self.client.request('/v1/runs'), [])

    def test_context_refresh_is_explicit(self):
        with patch.object(self.engine, 'scan') as scan:
            self.client.context(refresh=True)
            scan.assert_called_once()

    def test_schemas_are_available_through_the_installed_service(self):
        for name in ('device', 'platform', 'workflow'):
            document = self.client.schema(name)
            self.assertEqual(document['type'], 'object')
            self.assertIn('$schema', document)
        with self.assertRaises(IOPError):
            self.client.schema('../config')

    def test_repeated_registration_reuses_the_existing_driver(self):
        record = {'id': 'extra', 'driver': 'simulated', 'config': {'kind': 'stage'}}
        first = self.client.register(record)
        driver = self.engine.devices['extra']
        self.assertEqual(self.client.register(record), first)
        self.assertIs(self.engine.devices['extra'], driver)
        with self.assertRaises(IOPError):
            self.client.register(dict(record, config={'kind': 'meter'}))
        self.assertIs(self.engine.devices['extra'], driver)

    def test_remote_environment_never_starts_a_local_service(self):
        with patch.dict(os.environ, {'IOP_ENDPOINT': self.client.endpoint, 'IOP_TOKEN': self.config['token']}):
            with patch('ai4instruments.iop.cli.start', side_effect=AssertionError('Do not start locally')):
                client = desktop.ensure_service(self.engine.home)
        self.assertEqual(client.endpoint, self.client.endpoint)

    def test_agent_launcher_uses_exact_paths_and_does_not_export_credentials(self):
        config = agent_configuration(Path('/path with spaces/lab'), self.client.endpoint)
        entry = config['mcpServers']['iop']
        self.assertEqual(entry['command'], sys.executable)
        self.assertIn('/path with spaces/lab', entry['args'])
        self.assertEqual(entry['args'][-1], 'mcp')
        self.assertNotIn(self.config['token'], json.dumps(config))


class DeviceRecoveryCase(unittest.TestCase):
    def test_failed_startup_device_survives_other_registrations_and_can_reconnect(self):
        with tempfile.TemporaryDirectory() as directory:
            config = initialize(directory)
            config['discovery_interval'] = 0
            record = {'id': 'camera', 'driver': 'vendor-camera'}
            config['devices'] = [record]
            save_json(Path(directory) / 'config.json', config)
            with patch('ai4instruments.iop.engine.make_driver', side_effect=OSError('SDK is not installed')):
                engine = Engine(directory, config)
            try:
                engine.register({'id': 'axis', 'driver': 'simulated'})
                saved = json.loads((Path(directory) / 'config.json').read_text())
                self.assertEqual({d['id'] for d in saved['devices']}, {'camera', 'axis'})
                self.assertIn('camera', engine.offline)
                with patch('ai4instruments.iop.engine.make_driver', side_effect=lambda r, registry: Simulated(r['id'], {}, registry)):
                    self.assertEqual(engine.reconnect('camera')['state'], 'connected')
                self.assertIn('camera', engine.devices)
                self.assertNotIn('camera', engine.offline)
                self.assertFalse(engine.metrics()['errors'])
            finally:
                engine.close()


@unittest.skipUnless(importlib.util.find_spec('mcp'), 'Install the agent extra to exercise MCP')
class MCPCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def test_real_stdio_tools_configure_execute_and_retain_the_service(self):
        environment = dict(os.environ, IOP_TOKEN=self.config['token'])
        responses = queue.Queue()
        with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as error_log:
            process = subprocess.Popen([sys.executable, '-m', 'ai4instruments.iop', '--endpoint',
                                        self.client.endpoint, 'mcp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=error_log, text=True, encoding='utf-8', env=environment)
            def read():
                for line in process.stdout:
                    try:
                        responses.put(json.loads(line))
                    except ValueError:
                        responses.put({'unexpected_stdout': line})
            reader = threading.Thread(target=read, daemon=True)
            reader.start()
            sequence = 0
            def request(method, params):
                nonlocal sequence
                sequence += 1
                process.stdin.write(json.dumps({'jsonrpc':'2.0', 'id':sequence, 'method':method, 'params':params}) + '\n')
                process.stdin.flush()
                while True:
                    try:
                        response = responses.get(timeout=15)
                    except queue.Empty:
                        error_log.seek(0)
                        self.fail('MCP did not reply: ' + error_log.read())
                    self.assertNotIn('unexpected_stdout', response)
                    if response.get('id') == sequence:
                        self.assertNotIn('error', response, response)
                        return response['result']
            def call(name, arguments):
                value = request('tools/call', {'name':name, 'arguments':arguments})
                self.assertFalse(value.get('isError'), value)
                return value.get('structuredContent') or json.loads(value['content'][0]['text'])
            try:
                result = request('initialize', {'protocolVersion':'2025-11-25', 'capabilities':{},
                                                'clientInfo':{'name':'iop-integration', 'version':'1'}})
                self.assertEqual(result['serverInfo']['name'], 'IOP Runtime')
                process.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
                process.stdin.flush()
                tools = {t['name']: t for t in request('tools/list', {})['tools']}
                self.assertIn('submit_program', tools)
                self.assertIn('request_id', tools['submit_experiment']['inputSchema']['required'])
                context = call('lab_context', {})
                self.assertEqual(context['status']['devices'], 3)
                self.assertNotIn(self.config['token'], json.dumps(context))
                definition = {'schema_version':1, 'id':'mcp-bench', 'devices':['stage']}
                self.assertEqual(call('configure_platform', {'definition':definition})['revision'], 1)
                self.assertEqual(self.client.request('/v1/runs'), [])
                parameters = {'steps':[{'id':'read', 'device':'stage', 'operation':'position'}],
                              'platform':'mcp-bench', 'request_id':'mcp-read'}
                run = call('submit_experiment', parameters)
                self.assertEqual(call('submit_experiment', parameters)['id'], run['id'])
                self.client.run(run['id']).result(5)
                self.assertIn('read', call('experiment', {'run_id':run['id'], 'include_result':True})['result'])
                accepted = call('submit_experiment', {'steps':[{'id':'wait', 'device':'aux', 'operation':'wait',
                                 'arguments':{'duration':0.5}}], 'request_id':'continue-after-agent'})
                process.stdin.close()
                process.wait(timeout=10)
                self.assertEqual(self.client.run(accepted['id']).wait(5)['state'], 'completed')
                self.assertEqual(self.client.request('/v1/status')['devices'], 3)
                self.assertEqual(process.returncode, 0)
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
                reader.join(timeout=2)
                process.stdout.close()
                if not process.stdin.closed:
                    process.stdin.close()
