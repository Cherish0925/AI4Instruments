"""Read LXI DNS-SD advertisements without scanning unrelated network ports."""
import threading

SERVICES = ('_lxi._tcp.local.', '_scpi-raw._tcp.local.', '_hislip._tcp.local.', '_vxi-11._tcp.local.')


def announcement(service_type, info):
    def text(value):
        return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value or '')
    properties = {text(k).lower(): text(v) for k, v in info.properties.items()}
    addresses = info.parsed_scoped_addresses()
    host = next((a for a in addresses if ':' not in a), None) or info.server.rstrip('.')
    identity = {field: properties[key] for field, key in (
        ('manufacturer', 'manufacturer'), ('model', 'model'),
        ('serial_number', 'serialnumber'), ('firmware', 'firmwareversion')) if properties.get(key)}
    record = {'transport': 'lxi', 'address': info.name, 'name': identity.get('model') or info.name,
              'host': host, 'addresses': addresses, 'service_type': service_type, 'port': info.port,
              'identity': identity, 'identity_source': 'lxi-dns-sd', 'properties': properties,
              'status': 'discovered'}
    if service_type == '_scpi-raw._tcp.local.':
        record.update(transport='tcp', address=f'{host}:{info.port}', protocol='scpi',
                      connection={'transport': 'tcp', 'host': host, 'port': info.port})
    elif service_type in ('_hislip._tcp.local.', '_vxi-11._tcp.local.'):
        resource = properties.get('address')
        if resource and resource.upper().startswith('TCPIP') and resource.upper().endswith('::INSTR'):
            record.update(transport='visa', address=resource, protocol='scpi',
                          connection={'transport': 'visa', 'resource': resource})
    return record


def discover(duration=1.5):
    try:
        from zeroconf import Zeroconf, ServiceBrowser
    except ImportError:
        return [], [{'name': 'lxi-network', 'available': False, 'detail': 'Install the devices component.'}]
    found, lock = {}, threading.Lock()
    class Listener:
        def add_service(self, zc, kind, name):
            info = zc.get_service_info(kind, name, timeout=700)
            if info:
                with lock:
                    found[name] = announcement(kind, info)
        update_service = add_service
        def remove_service(self, zc, kind, name):
            with lock:
                found.pop(name, None)
    zc = Zeroconf()
    browser = None
    try:
        browser = ServiceBrowser(zc, list(SERVICES), listener=Listener())
        threading.Event().wait(duration)
    finally:
        if browser:
            browser.cancel()
        zc.close()
    return list(found.values()), [{'name': 'lxi-network', 'available': True}]
