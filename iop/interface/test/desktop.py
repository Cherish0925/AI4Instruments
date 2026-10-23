"""Open the real native window and confirm that closing it leaves experiments running."""
import os
import subprocess
import sys
import sysconfig
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import webview
from ai4instruments.iop import Client
from ai4instruments.iop.config import initialize, save_json
from ai4instruments.iop import desktop

errors = []
opened = []
with tempfile.TemporaryDirectory(prefix='iop-desktop-') as folder:
    home = Path(folder)
    config = initialize(home, True, 0)
    config['discovery_interval'] = 0
    save_json(home / 'config.json', config)
    service = subprocess.Popen([sys.executable, '-u', '-m', 'ai4instruments.iop', '--home', folder, 'serve'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    client = None
    try:
        line = service.stdout.readline()
        if 'http://' not in line:
            raise RuntimeError('Service did not start: ' + line)
        endpoint = line.split()[-1]
        client = Client(endpoint, token=config['token'])
        experiment = []

        def interact(window=None):
            window = window or webview.windows[0]
            try:
                if not window.events.loaded.wait(30):
                    raise RuntimeError('Desktop page did not load')
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    if window.evaluate_js("document.querySelector('#service-caption').textContent") == '运行服务在线':
                        break
                    time.sleep(.1)
                else:
                    raise RuntimeError('Desktop did not connect to the running service')
                assert window.evaluate_js("document.querySelector('#nav-devices').textContent") == '3'
                window.evaluate_js("document.querySelector('[data-view=devices]').click()")
                assert window.evaluate_js("document.querySelector('#view-title').textContent") == '仪器与软件'
                window.evaluate_js("document.querySelector('#mode-switch').click()")
                deadline = time.monotonic() + 5
                while not opened and time.monotonic() < deadline:
                    time.sleep(.1)
                assert opened and 'view=devices' in opened[0]
                experiment.append(client.submit([{'id':'wait','device':'stage','operation':'wait','arguments':{'duration':1}}]))
            except BaseException as error:
                errors.append(error)
            finally:
                window.destroy()

        with patch.object(desktop.webbrowser, 'open', side_effect=lambda url: opened.append(url)):
            if sys.platform == 'win32' and (sysconfig.get_platform() == 'win-arm64' or os.environ.get('PYTHONNET_RUNTIME') == 'coreclr'):
                from ai4instruments.iop import windows_desktop
                original = windows_desktop.open_window
                def start(*args, **kwargs):
                    return original(*args, **kwargs, on_loaded=interact)
                with patch.object(windows_desktop, 'open_window', side_effect=start):
                    desktop.launch(home, endpoint)
            else:
                original = webview.start
                def start(*args, **kwargs):
                    return original(interact, *args, **kwargs)
                with patch.object(webview, 'start', side_effect=start):
                    desktop.launch(home, endpoint)
        if errors:
            raise errors[0]
        assert experiment[0].wait(5)['state'] == 'completed'
        assert client.request('/v1/status')['devices'] == 3
        print('Native desktop passed: shared service, real page rendering, browser switch and experiment continuity after window close.')
    finally:
        if client:
            client.request('/v1/shutdown', {})
        try:
            service.wait(timeout=8)
        except subprocess.TimeoutExpired:
            service.kill(); service.wait()
        service.stdout.close(); service.stderr.close()
