"""Shared desktop/browser API and installed application entry points."""
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.request import urlopen
from urllib.parse import parse_qs, urlparse

from ai4instruments.iop import Client, desktop
from ai4instruments.iop.config import initialize
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server


class InterfaceCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = initialize(self.temp.name, True, 0)
        self.config['discovery_interval'] = 0
        self.engine = Engine(self.temp.name, self.config)
        self.server = Server(('127.0.0.1', 0), self.engine)
        self.engine.start()
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.client = Client(self.engine.endpoint, token=self.config['token'])

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.engine.close()
        self.temp.cleanup()

    def test_application_assets_and_service_identity(self):
        for path, media in [('/', 'text/html'), ('/ui/app.js', 'text/javascript'),
                            ('/ui/core.js', 'text/javascript'), ('/ui/app.css', 'text/css'),
                            ('/ui/mark.svg', 'image/svg+xml')]:
            with urlopen(self.engine.endpoint + path) as response:
                self.assertEqual(response.headers.get_content_type(), media)
                self.assertTrue(response.read())
        status = self.client.request('/v1/status')
        self.assertEqual(status['devices'], 3)
        self.assertIn('hostname', status)
        self.assertIn('uptime_s', status)

    def test_cached_inventory_does_not_repeat_discovery(self):
        self.engine.discovery = {'connections': [{'address': 'COM7'}], 'updated': 'saved'}
        with patch.object(self.engine, 'scan', return_value={'connections': []}) as scan:
            self.assertEqual(self.client.request('/v1/discovery?cached=true')['updated'], 'saved')
            scan.assert_not_called()
            self.client.request('/v1/discovery')
            scan.assert_called_once()

    def test_serial_registration_matches_inventory(self):
        self.client.register({'id': 'meter-serial', 'driver': 'scpi',
                              'config': {'transport': 'serial', 'port': 'COM7'}})
        inventory = {'connections': [{'transport': 'serial', 'address': 'COM7'}]}
        with patch('ai4instruments.iop.discovery.discover', return_value=inventory):
            result = self.client.request('/v1/discovery')['connections'][0]
        self.assertEqual(result['id'], 'meter-serial')
        self.assertEqual(result['status'], 'registered')

    def test_native_window_uses_requested_view(self):
        with patch.object(desktop, 'spawn', return_value={'opened': True, 'pid': 123}) as spawn:
            self.assertTrue(self.client.request('/v1/ui/desktop', {'view': 'devices'})['opened'])
            self.assertEqual(spawn.call_args.args, (self.engine.home, 'devices'))
        url = desktop.page_url(self.client, 'platforms', True)
        fields = parse_qs(urlparse(url).fragment)
        self.assertEqual(fields['view'], ['platforms'])
        self.assertEqual(fields['token'], [self.config['token']])
        self.assertNotIn(self.config['token'], urlparse(url).query)

    def test_summaries_and_separate_result(self):
        run = self.client.submit([{'id': 'read', 'device': 'stage', 'operation': 'position'}])
        expected = run.result(5)
        summary = self.client.request('/v1/runs?details=false')[0]
        self.assertNotIn('operations', summary)
        self.assertNotIn('result', summary)
        self.assertEqual(self.client.request('/v1/runs/' + run.id + '/result'), expected)


class LauncherCase(unittest.TestCase):
    def test_installed_application_entries_support_spaces(self):
        with tempfile.TemporaryDirectory(prefix='iop application ') as folder:
            home = Path(folder) / 'experiment data'
            initialize(home, False, 8765)
            entries = desktop.install_launchers(home, Path(folder) / 'application menu')
            self.assertEqual(len(entries), 2)
            for entry in entries:
                path = Path(entry)
                self.assertTrue(path.exists(), entry)
                if sys.platform == 'darwin':
                    text = (path / 'Contents/MacOS/iop').read_text()
                    self.assertIn(str(home), text)
                elif sys.platform != 'win32':
                    text = path.read_text()
                    self.assertIn('"' + str(home) + '"', text)
                    self.assertIn('Terminal=false', text)
