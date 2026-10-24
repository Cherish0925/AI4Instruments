"""Install an unpacked distribution and use its commands in an isolated directory."""
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'iop/release.json').read_text())['version']
archive, = (root / 'release').glob(f'IOP-{version}-*.zip')
with tempfile.TemporaryDirectory(prefix='iop install ') as temporary:
    temporary = Path(temporary).resolve()
    with zipfile.ZipFile(archive) as package:
        package.extractall(temporary / 'download')
    source, = (temporary / 'download').iterdir()
    prefix, home = temporary / 'application', temporary / 'laboratory'
    environment = dict(os.environ, IOP_INSTALL_DIR=str(prefix), IOP_HOME=str(home),
                       IOP_PYTHON=sys.executable, IOP_DESKTOP='0', IOP_AGENT='1')
    environment.pop('IOP_ENDPOINT', None)
    environment.pop('IOP_TOKEN', None)
    environment.pop('PYTHONPATH', None)
    command = (['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(source / 'install.ps1')]
               if sys.platform == 'win32' else ['sh', str(source / 'install.sh')])
    subprocess.run(command, env=environment, check=True, timeout=480)
    python = prefix / ('venv/Scripts/python.exe' if sys.platform == 'win32' else 'venv/bin/python')
    cli = [str(python), '-m', 'ai4instruments.iop']
    def run(*args):
        return subprocess.check_output([*cli, *args], env=environment, text=True, encoding='utf-8', timeout=30)
    original = (home / 'config.json').read_text(encoding='utf-8')
    config = json.loads(original)
    try:
        context = json.loads(run('context', '--start'))
        assert context['service']['version'] == json.loads((root / 'iop/release.json').read_text())['version']
        assert context['devices'] == []
        launch = json.loads(run('mcp-config'))['mcpServers']['iop']
        assert Path(launch['command']).samefile(python)
        assert str(home) in launch['args']
        assert config['token'] not in json.dumps(launch)
        subprocess.run([str(python), '-c', 'from ai4instruments.iop.context import schema_document; assert schema_document("platform")["title"]; assert schema_document("instrument-profile")["title"]; from ai4instruments.iop.identification import profiles; assert len(profiles({})) >= 4; import mcp'],
                       env=environment, check=True, timeout=30)
        assert (home / 'config.json').read_text(encoding='utf-8') == original
        print('Installed application passed: CLI, local service, Agent configuration, MCP dependency and packaged schemas.')
    finally:
        try:
            run('stop')
        finally:
            # Wait for the detached process to release its data and log handles before removing the installation.
            script = 'from ai4instruments.iop.config import InstanceLock; import sys; lock=InstanceLock(sys.argv[1]); lock.close()'
            for attempt in range(100):
                result = subprocess.run([str(python), '-c', script, str(home)], env=environment,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if result.returncode == 0:
                    try:
                        (home / 'service.log').unlink()
                        break
                    except OSError:
                        pass
                time.sleep(0.1)
            else:
                raise RuntimeError('Installed service did not exit')
