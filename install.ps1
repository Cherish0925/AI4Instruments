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
$IOPExtras = 'devices'
if ($env:IOP_AGENT -ne '0') { $IOPExtras += ',agent' }
if ($env:IOP_DESKTOP -eq '1') { $IOPExtras += ',desktop' }
& $InstalledPython -m pip install "${IOPSource}[$IOPExtras]"
if ($LASTEXITCODE -ne 0) { throw 'Could not install IOP' }
& $IOP init
if ($LASTEXITCODE -ne 0) { throw 'Could not initialize IOP' }
Write-Host "Installed. Start with: & '$IOP' start"
Write-Host "Open the platform with: & '$IOP' open"
Write-Host "Read laboratory setup: & '$IOP' context --start"
Write-Host "Agent connection settings: & '$IOP' mcp-config"

if ($env:IOP_DESKTOP -eq '1') {
    $IOPArchitecture = & $InstalledPython -c 'import sysconfig; print(sysconfig.get_platform())'
    if ($IOPArchitecture -eq 'win-arm64') {
        $IOPDotnetScript = Join-Path $InstallDir 'dotnet-install.ps1'
        Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $IOPDotnetScript
        foreach ($IOPFramework in @('dotnet', 'windowsdesktop')) {
            & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $IOPDotnetScript -Runtime $IOPFramework -Channel 10.0 -Architecture arm64 -InstallDir (Join-Path $InstallDir 'dotnet') -NoPath
            if ($LASTEXITCODE -ne 0) { throw 'Could not install the ARM64 desktop runtime' }
        }
    }
    & $IOP shortcuts
    if ($LASTEXITCODE -ne 0) { throw 'Could not create application shortcuts' }
    Write-Host "Open IOP Runtime from the Start menu, or run: & '$IOP' desktop"
}
