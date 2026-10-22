"""User-session startup using each operating system's service manager."""
import os
import plistlib
import subprocess
import sys
from pathlib import Path


def systemd_unit(python, home):
    def quote(value):
        return '"' + str(value).replace('\\','\\\\').replace('"','\\"').replace('%','%%') + '"'
    return '[Unit]\nDescription=IOP instrument service\nAfter=network.target\n\n[Service]\nType=simple\nExecStart=' + ' '.join(quote(s) for s in [python,'-m','ai4instruments.iop','--home',home,'serve']) + '\nRestart=on-failure\nRestartSec=3\n\n[Install]\nWantedBy=default.target\n'


def launchd_plist(python, home):
    return plistlib.dumps({'Label':'org.ai4instruments.iop',
        'ProgramArguments':[str(python),'-m','ai4instruments.iop','--home',str(home),'serve'],
        'RunAtLoad':True, 'KeepAlive':{'SuccessfulExit':False},
        'StandardOutPath':str(Path(home)/'service.log'), 'StandardErrorPath':str(Path(home)/'service.log')})


def windows_script(python, home):
    def ps(s):
        return "'" + str(s).replace("'","''") + "'"
    arguments = subprocess.list2cmdline(['-m','ai4instruments.iop','--home',str(home),'serve'])
    return ("$ErrorActionPreference = 'Stop'\n"
        "$action = New-ScheduledTaskAction -Execute " + ps(python) + ' -Argument ' + ps(arguments) + '\n'
        "$trigger = New-ScheduledTaskTrigger -AtLogOn -User ([Security.Principal.WindowsIdentity]::GetCurrent().Name)\n"
        "$settings = New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries\n"
        "Register-ScheduledTask -TaskName 'AI4Instruments-IOP' -Action $action -Trigger $trigger -Settings $settings -RunLevel Limited -Force | Out-Null\n"
        "Start-ScheduledTask -TaskName 'AI4Instruments-IOP'\n")


def install(home):
    if sys.platform == 'win32':
        path = Path(home)/'install-service.ps1'
        path.write_text(windows_script(sys.executable, home), encoding='utf-8-sig')
        subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(path)], check=True)
        return 'Windows login task: AI4Instruments-IOP'
    if sys.platform == 'darwin':
        path = Path.home()/'Library/LaunchAgents/org.ai4instruments.iop.plist'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(launchd_plist(sys.executable, home))
        domain = 'gui/' + str(os.getuid())
        subprocess.run(['launchctl','bootout',domain,str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['launchctl','bootstrap',domain,str(path)], check=True)
        return str(path)
    if sys.platform.startswith('linux'):
        path = Path.home()/'.config/systemd/user/iop.service'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(systemd_unit(sys.executable, home), encoding='utf-8')
        subprocess.run(['systemctl','--user','daemon-reload'], check=True)
        subprocess.run(['systemctl','--user','enable','--now','iop.service'], check=True)
        return str(path)
    raise RuntimeError('Use iop start on this operating system')


def uninstall():
    if sys.platform == 'win32':
        subprocess.run(['powershell.exe','-NoProfile','-Command',"Unregister-ScheduledTask -TaskName 'AI4Instruments-IOP' -Confirm:$false"], check=True)
    elif sys.platform == 'darwin':
        path = Path.home()/'Library/LaunchAgents/org.ai4instruments.iop.plist'
        subprocess.run(['launchctl','bootout','gui/'+str(os.getuid()),str(path)], check=True)
        path.unlink(missing_ok=True)
    elif sys.platform.startswith('linux'):
        subprocess.run(['systemctl','--user','disable','--now','iop.service'], check=True)
        (Path.home()/'.config/systemd/user/iop.service').unlink(missing_ok=True)
        subprocess.run(['systemctl','--user','daemon-reload'], check=True)
