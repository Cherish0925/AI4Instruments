$ErrorActionPreference = 'Stop'
$InstallDir = if ($env:IOP_INSTALL_DIR) { $env:IOP_INSTALL_DIR } else { Join-Path $env:LOCALAPPDATA 'AI4Instruments' }
$Python = if ($env:IOP_PYTHON) { $env:IOP_PYTHON } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
& $Python -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10 or later is required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 or later is required' }
& $Python -m venv (Join-Path $InstallDir 'venv')
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment' }
$InstalledPython = Join-Path $InstallDir 'venv\Scripts\python.exe'
$IOP = Join-Path $InstallDir 'venv\Scripts\iop.exe'
& $InstalledPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare pip' }
$IOPWheel = Get-ChildItem (Join-Path $PSScriptRoot 'dist\*.whl') -ErrorAction SilentlyContinue | Select-Object -First 1
$IOPSource = if ($IOPWheel) { $IOPWheel.FullName } else { $PSScriptRoot }
$IOPExtras = if ($env:IOP_DESKTOP -eq '1') { 'devices,desktop' } else { 'devices' }
& $InstalledPython -m pip install "${IOPSource}[$IOPExtras]"
if ($LASTEXITCODE -ne 0) { throw 'Could not install IOP' }
& $IOP init
Write-Host "Installed. Start with: & '$IOP' start"
Write-Host "Open the platform with: & '$IOP' open"

if ($env:IOP_DESKTOP -eq '1') {
    & $IOP shortcuts
    if ($LASTEXITCODE -ne 0) { throw 'Could not create application shortcuts' }
    Write-Host "Open IOP Runtime from the Start menu, or run: & '$IOP' desktop"
}
