"""Installed driver packages advertise names without changing the runtime."""
from importlib.metadata import entry_points


def adapters():
    builtin = [
        ('scpi', 'SCPI over TCP, serial and VISA'),
        ('modbus', 'Modbus TCP and RTU'),
        ('http', 'HTTP JSON operations'),
        ('command', 'Executable programs and command-line solvers'),
        ('process', 'Independent SDK workers using JSON lines'),
        ('simulated', 'In-process demonstration instruments'),
        ('simulated-lab', 'Simulated laboratory components'),
    ]
    result = [{'name': name, 'source': 'builtin', 'description': description} for name, description in builtin]
    result[0]['connection_parameters'] = {
        'common': {'timeout': {'type':'number', 'default':5, 'unit':'s'},
                   'termination': {'type':'string', 'default':'\n'}},
        'tcp': {'host': {'type':'string', 'required':True}, 'port': {'type':'integer', 'default':5025},
                'source_address': {'type':'string', 'description':'Local IPv4 or IPv6 address of the instrument-facing network interface; omit to use system routing'}},
        'serial': {'port': {'type':'string', 'required':True}, 'baudrate': {'type':'integer', 'default':9600},
                   'bytesize': {'type':'integer', 'default':8, 'enum':[5,6,7,8]},
                   'parity': {'type':'string', 'default':'N', 'enum':['N','E','O','M','S']},
                   'stopbits': {'type':'number', 'default':1, 'enum':[1,1.5,2]},
                   'xonxoff': {'type':'boolean', 'default':False}, 'rtscts': {'type':'boolean', 'default':False},
                   'dsrdtr': {'type':'boolean', 'default':False}},
        'visa': {'resource': {'type':'string', 'required':True}, 'backend': {'type':'string'}}}
    for entry in entry_points(group='ai4instruments.drivers'):
        result.append({'name': entry.name, 'source': 'package', 'entry_point': entry.value,
                       'package': entry.dist.metadata['Name'] if entry.dist else None,
                       'version': entry.dist.version if entry.dist else None})
    return result
