"""Fetch a pinned redistributable Python and build the offline dependency directory."""
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
machine = platform.machine().lower()
arch = 'aarch64' if machine in ('arm64', 'aarch64') else 'x86_64'
target = arch + {'Windows': '-pc-windows-msvc', 'Darwin': '-apple-darwin', 'Linux': '-unknown-linux-gnu'}[platform.system()]
sources = json.loads((root / 'iop/python-distributions.json').read_text())
source, = [s for s in sources if target + '-install_only_' in s['name']]
directory = root / 'build' / 'portable'
directory.mkdir(parents=True, exist_ok=True)
archive = directory / 'python.tar.gz'
with urlopen(source['url'], timeout=120) as response, archive.open('wb') as output:
    while data := response.read(1024 * 1024):
        output.write(data)
if hashlib.sha256(archive.read_bytes()).hexdigest() != source['sha256']:
    raise RuntimeError('Python download is incomplete or differs from the published distribution')
(directory / 'source.json').write_text(json.dumps(source, indent=2) + '\n')
wheel, = (root / 'dist').glob('*.whl')
# Build missing platform wheels here, so installation never needs a compiler.
subprocess.run([sys.executable, '-m', 'pip', 'wheel', '--prefer-binary', '--wheel-dir', str(directory / 'wheels'),
                str(wheel) + '[devices,agent]', 'pip'], check=True)
print('Prepared Python and offline Runtime/Agent dependencies for ' + target)
