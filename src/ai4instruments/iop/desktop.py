"""Native desktop window and installed launchers for the persistent IOP service."""
from __future__ import annotations
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import sysconfig
import tempfile
import webbrowser
from pathlib import Path
from urllib.parse import urlencode
from .client import Client
from .config import home_path


def available():
    return importlib.util.find_spec('webview') is not None


def has_display():
    return sys.platform != 'linux' or bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))


def page_url(client, view='overview', desktop=False):
    fields = {'token': client.token, 'view': view}
    if desktop:
        fields['desktop'] = '1'
    return client.endpoint + '/#' + urlencode(fields)


def ensure_service(home, endpoint=None):
    if endpoint:
        client = Client(endpoint, home=home)
        client.request('/v1/status')
        return client
    from .cli import start
    start(home)
    return Client(home=home)


def open_browser(home, endpoint=None, view='overview'):
    client = ensure_service(home, endpoint)
    webbrowser.open(page_url(client, view))


def launch(home, endpoint=None, view='overview'):
    if not available():
        raise RuntimeError('Install the desktop component with install-desktop.ps1 (Windows) or install-desktop.sh (macOS / Linux).')
    if sys.platform == 'win32' and (sysconfig.get_platform() == 'win-arm64' or os.environ.get('PYTHONNET_RUNTIME') == 'coreclr'):
        from pythonnet import load
        options = {'runtime_config': str(Path(__file__).with_name('desktop.runtimeconfig.json'))}
        runtime = Path(os.environ.get('IOP_DESKTOP_DOTNET_ROOT', Path(sys.prefix).parent / 'dotnet'))
        if runtime.is_dir():
            options['dotnet_root'] = str(runtime)
        load('coreclr', **options)
        import clr
        # CoreCLR separates desktop drawing and system events into their own assemblies.
        for assembly in ('System.Windows.Forms', 'System.Drawing.Primitives',
                         'System.Drawing.Common', 'Microsoft.Win32.SystemEvents'):
            clr.AddReference(assembly)
    import webview
    client = ensure_service(home, endpoint)

    class Bridge:
        def open_browser(self, selected='overview'):
            webbrowser.open(page_url(client, selected))
            return True

    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.create_window('IOP Runtime', page_url(client, view, True), js_api=Bridge(),
                          width=1360, height=900, min_size=(860, 620),
                          background_color='#f7f7f5', text_select=True)
    webview.start(private_mode=False, storage_path=str(Path(home) / 'desktop'))


def spawn(home, view='overview'):
    if not available():
        raise ValueError('The desktop component is not installed. Run the desktop installer on this computer.')
    if not has_display():
        raise ValueError('This service has no desktop session. Open IOP Desktop on your computer and connect to the service.')
    python = Path(sys.executable)
    if sys.platform == 'win32' and python.with_name('pythonw.exe').exists():
        python = python.with_name('pythonw.exe')
    options = {'creationflags': subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == 'win32' else {'start_new_session': True}
    with open(Path(home) / 'desktop.log', 'ab') as log:
        process = subprocess.Popen([str(python), '-m', 'ai4instruments.iop', '--home', str(home),
                                    'desktop', '--view', view], stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
    return {'opened': True, 'pid': process.pid}


def install_launchers(home, destination=None):
    """Create an OS application entry and a separate browser entry for this installation."""
    home = home_path(home)
    python = Path(sys.executable)
    written = []
    if sys.platform == 'win32':
        folder = Path(destination) if destination else Path(os.environ['APPDATA']) / 'Microsoft/Windows/Start Menu/Programs/IOP Runtime'
        folder.mkdir(parents=True, exist_ok=True)
        executable = python.with_name('pythonw.exe')
        if not executable.exists(): executable = python
        records = []
        for label, command in [('IOP Runtime', 'desktop'), ('IOP Browser', 'open')]:
            records.append({'path':str(folder / (label + '.lnk')), 'target':str(executable),
                            'icon':str(Path(__file__).with_name('ui') / 'mark.ico'),
                            'arguments':subprocess.list2cmdline(['-m', 'ai4instruments.iop', '--home', str(home), command])})
        definitions = home / 'desktop-shortcuts.json'
        definitions.write_text(json.dumps(records), encoding='utf-8')
        script = "param([string]$Definitions)\n$ErrorActionPreference='Stop'\n$shell=New-Object -ComObject WScript.Shell\n$items=Get-Content -Raw -Encoding UTF8 -LiteralPath $Definitions | ConvertFrom-Json\nforeach($item in $items){$s=$shell.CreateShortcut($item.path);$s.TargetPath=$item.target;$s.Arguments=$item.arguments;$s.IconLocation=$item.icon;$s.Description='IOP Runtime';$s.Save()}\n"
        with tempfile.TemporaryDirectory(prefix='iop-shortcuts-') as folder:
            script_file = Path(folder) / 'shortcuts.ps1'
            script_file.write_text(script, encoding='utf-8')
            subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                            str(script_file), '-Definitions', str(definitions)], check=True)
        written = [record['path'] for record in records]
    elif sys.platform == 'darwin':
        import plistlib
        import shutil
        folder = Path(destination) if destination else Path.home() / 'Applications'
        for label, command in [('IOP Runtime', 'desktop'), ('IOP Browser', 'open')]:
            app = folder / (label + '.app') / 'Contents'; macos = app / 'MacOS'; macos.mkdir(parents=True, exist_ok=True)
            executable = macos / 'iop'
            executable.write_text('#!/bin/sh\nexec ' + shlex.join([str(python), '-m', 'ai4instruments.iop', '--home', str(home), command]) + '\n')
            executable.chmod(0o755)
            resources = app / 'Resources'; resources.mkdir(exist_ok=True)
            shutil.copy2(Path(__file__).with_name('ui') / 'mark.icns', resources / 'mark.icns')
            with (app / 'Info.plist').open('wb') as file:
                plistlib.dump({'CFBundleName':label, 'CFBundleDisplayName':label, 'CFBundleExecutable':'iop',
                              'CFBundleIdentifier':'org.ai4instruments.iop.' + command, 'CFBundlePackageType':'APPL',
                              'NSHighResolutionCapable':True, 'CFBundleIconFile':'mark.icns'}, file)
            written.append(str(app.parent))
    else:
        folder = Path(destination) if destination else Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'applications'
        folder.mkdir(parents=True, exist_ok=True)
        def quote(value):
            return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%') + '"'
        for label, command in [('IOP Runtime', 'desktop'), ('IOP Browser', 'open')]:
            path = folder / ('iop-' + command + '.desktop')
            argv = ' '.join(quote(v) for v in [python, '-m', 'ai4instruments.iop', '--home', home, command])
            path.write_text('[Desktop Entry]\nType=Application\nName=' + label + '\nExec=' + argv + '\nIcon=' + str(Path(__file__).with_name('ui') / 'mark.svg') + '\nTerminal=false\nCategories=Science;Education;\n', encoding='utf-8')
            path.chmod(0o755); written.append(str(path))
    return written
