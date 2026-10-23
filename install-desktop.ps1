$ErrorActionPreference = 'Stop'
$env:IOP_DESKTOP = '1'
try { & (Join-Path $PSScriptRoot 'install.ps1') }
finally { Remove-Item Env:IOP_DESKTOP -ErrorAction SilentlyContinue }
