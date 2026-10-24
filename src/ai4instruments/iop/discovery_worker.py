"""Run an installed SDK's enumeration in a separate, short-lived process."""
import contextlib
import json
import sys
from importlib.metadata import entry_points


def nidaqmx_devices():
    from nidaqmx.system import System
    rows = []
    for device in System.local().devices:
        identity = {'manufacturer': 'NI', 'model': device.product_type,
                    'serial_number': format(device.dev_serial_num, 'X')}
        channels = {}
        for group in ('ai_physical_chans', 'ao_physical_chans', 'di_lines', 'do_lines', 'ci_physical_chans', 'co_physical_chans'):
            channels[group] = [c.name for c in getattr(device, group)]
        rows.append({'transport': 'sdk', 'address': 'nidaqmx:' + device.name, 'name': device.product_type,
                     'identity': identity, 'identity_source': 'nidaqmx', 'sdk': 'nidaqmx',
                     'channels': channels, 'simulated': device.is_simulated,
                     'documentation': ['https://nidaqmx-python.readthedocs.io/en/stable/'],
                     'status': 'discovered'})
    return rows


def pylon_devices():
    from pypylon import pylon
    rows = []
    for device in pylon.TlFactory.GetInstance().EnumerateDevices():
        identity = {'manufacturer': device.GetVendorName(), 'model': device.GetModelName(),
                    'serial_number': device.GetSerialNumber()}
        rows.append({'transport': 'sdk', 'address': 'pylon:' + device.GetFullName(),
                     'name': device.GetFriendlyName(), 'identity': identity, 'identity_source': 'pylon',
                     'sdk': 'pypylon', 'device_class': device.GetDeviceClass(),
                     'documentation': ['https://docs.baslerweb.com/pythonProgGuide'], 'status': 'discovered'})
    return rows


def run(name):
    if name == '_lxi':
        from .network_discovery import discover
        return discover()
    if name == '_visa':
        from .discovery import _visa_inventory
        return _visa_inventory()
    if name == 'nidaqmx':
        return nidaqmx_devices()
    if name == 'pypylon':
        return pylon_devices()
    entries = [e for e in entry_points(group='ai4instruments.discovery') if e.name == name]
    if len(entries) != 1:
        raise ValueError('Discovery provider must have one installed entry point: ' + name)
    rows = entries[0].load()()
    if not isinstance(rows, list) or any(not isinstance(r, dict) or not r.get('transport') or not r.get('address') for r in rows):
        raise ValueError('Discovery providers return a list of connection descriptions with transport and address.')
    return rows


if __name__ == '__main__':
    with contextlib.redirect_stdout(sys.stderr):
        result = run(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
