$ErrorActionPreference = 'Stop'
$InstallDir = if ($env:IOP_INSTALL_DIR) { $env:IOP_INSTALL_DIR } else { Join-Path $env:LOCALAPPDATA 'AI4Instruments' }
$PythonArchive = Join-Path $PSScriptRoot 'runtime\python.tar.gz'
if ((Test-Path $PythonArchive) -and -not $env:IOP_PYTHON) {
    $PythonDir = Join-Path $InstallDir 'runtime\0.8.2'
    New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null
    & tar.exe -xzf $PythonArchive -C $PythonDir
    if ($LASTEXITCODE -ne 0) { throw 'Could not unpack the included Python' }
    $Python = Join-Path $PythonDir 'python\python.exe'
    $BundledPython = $true
} else {
    $Python = if ($env:IOP_PYTHON) { $env:IOP_PYTHON } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
}
& $Python -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10 or later is required"'
if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 or later is required' }
$PreviousPython = Join-Path $InstallDir 'venv\Scripts\python.exe'
if (Test-Path $PreviousPython) {
    & $PreviousPython (Join-Path $PSScriptRoot 'scripts\prepare_iop_upgrade.py')
    if ($LASTEXITCODE -ne 0) { throw 'The previous installation is still in use' }
    & $Python -m venv --upgrade (Join-Path $InstallDir 'venv')
} else {
    & $Python -m venv (Join-Path $InstallDir 'venv')
}
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment' }
$InstalledPython = Join-Path $InstallDir 'venv\Scripts\python.exe'
$IOP = Join-Path $InstallDir 'venv\Scripts\iop.exe'
$OfflineWheels = Join-Path $PSScriptRoot 'runtime\wheels'
if (Test-Path $OfflineWheels) {
    & $InstalledPython -m pip install --no-index --find-links $OfflineWheels --upgrade pip
} else {
    & $InstalledPython -m pip install --upgrade pip
}
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare pip' }
$IOPWheel = Get-ChildItem (Join-Path $PSScriptRoot 'dist\*.whl') -ErrorAction SilentlyContinue | Select-Object -First 1
$IOPSource = if ($IOPWheel) { $IOPWheel.FullName } else { $PSScriptRoot }
$IOPExtras = 'devices'
if ($env:IOP_AGENT -ne '0') { $IOPExtras += ',agent' }
if ($env:IOP_DESKTOP -eq '1') { $IOPExtras += ',desktop' }
if ((Test-Path $OfflineWheels) -and $BundledPython -and $env:IOP_DESKTOP -ne '1') {
    & $InstalledPython -m pip install --no-index --find-links $OfflineWheels "${IOPSource}[$IOPExtras]"
} else {
    & $InstalledPython -m pip install --prefer-binary "${IOPSource}[$IOPExtras]"
}
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
