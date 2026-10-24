"""Create a system-specific install archive from its already-built wheel."""
from pathlib import Path
import json
import platform
import zipfile

root = Path(__file__).resolve().parents[1]
version = json.loads((root / 'iop/release.json').read_text())['version']
wheel, = (root / 'dist').glob(f'ai4instruments-{version}-*.whl')
system = {'Darwin':'macos','Windows':'windows','Linux':'linux'}[platform.system()]
arch = {'AMD64':'x86_64','ARM64':'arm64','aarch64':'arm64'}.get(platform.machine(), platform.machine())
name = f'IOP-{version}-{system}-{arch}'
output = root / 'release'; output.mkdir(exist_ok=True)
with zipfile.ZipFile(output / (name + '.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
    archive.write(wheel, name + '/dist/' + wheel.name)
    portable = root / 'build' / 'portable'
    if not (portable / 'python.tar.gz').is_file():
        raise RuntimeError('Run scripts/prepare_iop_python.py before building a distribution')
    for file in portable.rglob('*'):
        if file.is_file():
            archive.write(file, name + '/runtime/' + file.relative_to(portable).as_posix())
    for filename in ('install.sh','install.ps1','install-desktop.sh','install-desktop.ps1','LICENSE'):
        archive.write(root / filename, name + '/' + filename)
    archive.write(root / 'scripts/prepare_iop_upgrade.py', name + '/scripts/prepare_iop_upgrade.py')
    for document in (root / 'iop').glob('*.md'):
        archive.write(document, name + '/iop/' + document.name)
    for folder in ('iop/examples','iop/schema','iop/performance','iop/interface/screenshots','docs/runtime','examples/iop'):
        for file in (root / folder).rglob('*'):
            if file.is_file() and '__pycache__' not in file.parts:
                archive.write(file,name + '/' + file.relative_to(root).as_posix())
    archive.writestr(name + '/README.txt', f'''IOP {version}

Python, the Rust executor and Runtime/Agent dependencies are included.
Runtime, browser interface and Agent installation work without a system Python or package downloads.
Linux/macOS/WSL: sh install.sh
Windows: powershell -NoProfile -ExecutionPolicy Bypass -File .\\install.ps1
The installer prints the installed command paths.
Agent MCP connection: iop mcp-config
Laboratory configuration: iop context --start

Desktop installation: install-desktop.sh or install-desktop.ps1 (downloads the native UI dependencies)
Open IOP Runtime from the system application menu, or run iop desktop.
Browser: iop open
Both start or connect to the same persistent service.
The Agent component is included by default. Set IOP_AGENT=0 to omit it.
Platform setup and usage:
https://github.com/Cherish0925/AI4Instruments/tree/main/iop
''')
print(output / (name + '.zip'))
