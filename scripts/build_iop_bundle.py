"""Create a system-specific install archive from its already-built wheel."""
from pathlib import Path
import json
import platform
import zipfile

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'iop/release.json').read_text())['version']
wheel, = (root / 'dist').glob('*.whl')
system = {'Darwin':'macos','Windows':'windows','Linux':'linux'}[platform.system()]
arch = {'AMD64':'x86_64','aarch64':'arm64'}.get(platform.machine(), platform.machine())
name = f'IOP-{version}-{system}-{arch}'
output = root / 'release'; output.mkdir(exist_ok=True)
with zipfile.ZipFile(output / (name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.write(wheel, name + '/dist/' + wheel.name)
    for filename in ('install.sh','install.ps1','LICENSE'):
        archive.write(root / filename, name + '/' + filename)
    for folder in ('iop/examples','iop/schema','examples/iop'):
        for file in (root / folder).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file,name + '/' + file.relative_to(root).as_posix())
    archive.writestr(name + '/README.txt', f'''IOP {version}

Python 3.10+ is required. This archive includes the native Rust executor.
Linux/macOS/WSL: sh install.sh
Windows: powershell -NoProfile -ExecutionPolicy Bypass -File .\\install.ps1
The installer prints the installed command paths.

Start: iop init, iop start, iop open
Platform setup and usage:
https://github.com/Cherish0925/AI4Instruments/tree/main/iop
''')
print(output / (name + '.zip'))
