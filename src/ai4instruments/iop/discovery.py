"""Inventory visible connections without assuming a device's command language."""
import json
import platform
import subprocess
import os
import shutil
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def _command(args):
    return subprocess.check_output(args, text=True, encoding="utf-8", errors="replace", timeout=15, stderr=subprocess.DEVNULL)


def _serial():
    found, providers = [], []
    try:
        from serial.tools import list_ports
        for port in list_ports.comports():
            found.append({"transport":"serial", "address":port.device, "name":port.description,
                          "manufacturer":port.manufacturer, "serial_number":port.serial_number,
                          "vid":port.vid, "pid":port.pid, "status":"discovered"})
        providers.append({"name":"serial", "available":True})
    except ImportError:
        providers.append({"name":"serial", "available":False, "detail":"Install ai4instruments[devices]"})
    except Exception as error:
        providers.append({"name":"serial", "available":False, "detail":str(error)})
    return found, providers


def _visa():
    found, providers = [], []
    try:
        import pyvisa
        rm = pyvisa.ResourceManager()
        try:
            for address in rm.list_resources("?*"):
                found.append({"transport":"visa", "address":address, "name":address, "status":"discovered"})
        finally:
            rm.close()
        providers.append({"name":"visa", "available":True})
    except ImportError:
        providers.append({"name":"visa", "available":False, "detail":"Install ai4instruments[devices]"})
    except Exception as error:
        providers.append({"name":"visa", "available":False, "detail":str(error)})
    return found, providers


def _usb():
    found, providers = [], []
    try:
        system = platform.system()
        if system == "Linux":
            for device in Path('/sys/bus/usb/devices').glob('*'):
                if not (device / 'idVendor').exists():
                    continue
                def read(name):
                    p = device / name
                    return p.read_text().strip() if p.exists() else None
                found.append({"transport":"usb", "address":device.name, "name":read('product') or device.name,
                              "manufacturer":read('manufacturer'), "serial_number":read('serial'),
                              "vid":read('idVendor'), "pid":read('idProduct'), "status":"discovered"})
        elif system == "Windows":
            text = _command(['powershell.exe','-NoProfile','-Command',
                             "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); @(Get-PnpDevice -PresentOnly | Where-Object {$_.InstanceId -like 'USB*'} | Select-Object FriendlyName,InstanceId,Class,Status) | ConvertTo-Json -Compress"])
            rows = json.loads(text or '[]')
            for row in rows if isinstance(rows, list) else [rows]:
                hardware_id = row['InstanceId']
                vid = re.search(r'VID_([0-9A-F]{4})', hardware_id, re.I)
                pid = re.search(r'PID_([0-9A-F]{4})', hardware_id, re.I)
                found.append({"transport":"usb", "address":row['InstanceId'], "name":row.get('FriendlyName'),
                              "vid":int(vid[1], 16) if vid else None, "pid":int(pid[1], 16) if pid else None,
                              "device_class":row.get('Class'), "status":"discovered"})
        elif system == "Darwin":
            tree = json.loads(_command(['system_profiler','SPUSBDataType','-json']))
            def walk(items):
                for item in items:
                    if 'vendor_id' in item:
                        found.append({"transport":"usb", "address":item.get('location_id',item.get('_name')),
                                      "name":item.get('_name'), "manufacturer":item.get('manufacturer'),
                                      "serial_number":item.get('serial_num'), "vid":item.get('vendor_id'),
                                      "pid":item.get('product_id'), "status":"discovered"})
                    walk(item.get('_items', []))
            walk(tree.get('SPUSBDataType', []))
        providers.append({"name":"usb-inventory", "available":system in {'Linux','Windows','Darwin'}})
    except Exception as error:
        providers.append({"name":"usb-inventory", "available":False, "detail":str(error)})
    return found, providers


def _software(software_profiles):
    found, providers = [], []
    for profile in software_profiles:
        candidates = profile.get('executables', [])
        if not isinstance(candidates, list) or any(not isinstance(v, str) for v in candidates):
            raise ValueError('Software discovery executables must be a list of names or paths')
        for candidate in candidates:
            path = shutil.which(os.path.expandvars(os.path.expanduser(candidate)))
            if path:
                found.append({'transport': 'command', 'program': profile['id'], 'name': profile.get('name', profile['id']),
                              'address': str(Path(path).resolve()), 'status': 'discovered'})
                break
    providers.append({'name': 'software-profiles', 'available': True, 'configured': len(software_profiles)})
    return found, providers


def connection_key(candidate):
    transport, address = candidate.get('transport'), str(candidate.get('address', ''))
    if transport == 'serial' and re.fullmatch(r'COM\d+', address, re.I):
        address = address.upper()
    if transport == 'visa':
        match = re.fullmatch(r'ASRL(\d+)::INSTR', address, re.I)
        if match and platform.system() == 'Windows':
            return 'serial:COM' + match[1]
    return str(transport) + ':' + address


def device_connection(record):
    config = record.get('config', {})
    transport = config.get('transport', 'tcp')
    if record.get('driver') not in ('scpi', 'modbus'):
        return None
    address = config.get('resource') if transport == 'visa' else config.get('port')
    if transport == 'tcp':
        address = str(config.get('host')) + ':' + str(config.get('port', 5025 if record['driver'] == 'scpi' else 502))
    return connection_key({'transport': transport, 'address': address})


def normalize(inventory):
    """Keep raw interfaces available; group only proven aliases for presentation."""
    groups = {}
    for candidate in inventory['connections']:
        candidate['category'] = 'usb' if candidate.get('transport') == 'usb' else 'interface'
        candidate['connection_key'] = connection_key(candidate)
        groups.setdefault(candidate['connection_key'], []).append(candidate)
    inventory['groups'] = [
        {**min(rows, key=lambda c: c.get('transport') == 'visa'), 'interfaces': rows}
        for rows in groups.values()
    ]
    inventory['summary'] = {
        'interfaces': sum(g['category'] == 'interface' for g in inventory['groups']),
        'usb_entries': sum(g['category'] == 'usb' for g in inventory['groups']),
    }
    return inventory


def discover(software_profiles=()):
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix='iop-inventory') as pool:
        jobs = [pool.submit(_serial), pool.submit(_visa), pool.submit(_usb),
                pool.submit(_software, software_profiles)]
        results = []
        for name, job in zip(('serial', 'visa', 'usb-inventory', 'software-profiles'), jobs):
            try:
                results.append(job.result())
            except Exception as error:
                results.append(([], [{'name': name, 'available': False, 'detail': str(error)}]))
    return normalize({'connections': [c for rows, _ in results for c in rows],
                      'providers': [p for _, rows in results for p in rows],
                      'duration_s': round(time.monotonic() - started, 3)})


def match_profiles(inventory, profiles):
    """Bind an installed description to a discovered connection by explicit fields."""
    matches = []
    for profile in profiles:
        match = profile.get('match', {})
        if 'transport' not in match:
            raise ValueError('A discovery profile must name its transport')
        for candidate in inventory['connections']:
            def comparable(key, value):
                if key in ('vid', 'pid') and isinstance(value, str):
                    try:
                        return int(value.split()[0], 16)
                    except ValueError:
                        pass
                return value
            if not all(comparable(key, candidate.get(key)) == comparable(key, value) for key,value in match.items()):
                continue
            def fill(value):
                if isinstance(value, str):
                    for key, replacement in candidate.items():
                        value = value.replace('{' + key + '}', str(replacement))
                    return value
                if isinstance(value, dict):return {k:fill(v) for k,v in value.items()}
                if isinstance(value, list):return [fill(v) for v in value]
                return value
            matches.append(fill(profile['device']))
    return matches
