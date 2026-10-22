"""Inventory visible connections without assuming a device's command language."""
import json
import platform
import subprocess
from pathlib import Path


def _command(args):
    return subprocess.check_output(args, text=True, encoding="utf-8", errors="replace", timeout=15, stderr=subprocess.DEVNULL)


def discover():
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
                found.append({"transport":"usb", "address":row['InstanceId'], "name":row.get('FriendlyName'),
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
    return {"connections":found, "providers":providers}


def match_profiles(inventory, profiles):
    """Bind an installed description to a discovered connection by explicit fields."""
    matches = []
    for profile in profiles:
        match = profile.get('match', {})
        if 'transport' not in match:
            raise ValueError('A discovery profile must name its transport')
        for candidate in inventory['connections']:
            if not all(candidate.get(key) == value for key,value in match.items()):
                continue
            def fill(value):
                if isinstance(value, str):return value.format_map(candidate)
                if isinstance(value, dict):return {k:fill(v) for k,v in value.items()}
                if isinstance(value, list):return [fill(v) for v in value]
                return value
            matches.append(fill(profile['device']))
    return matches
