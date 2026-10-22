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
    for entry in entry_points(group='ai4instruments.drivers'):
        result.append({'name': entry.name, 'source': 'package', 'entry_point': entry.value,
                       'package': entry.dist.metadata['Name'] if entry.dist else None,
                       'version': entry.dist.version if entry.dist else None})
    return result
