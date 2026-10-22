"""Installed driver example: connect a vendor SDK at this one interface."""
from ai4instruments.iop import Driver


class Temperature(Driver):
    def describe(self):
        return {'name':'Temperature channel', 'mode':'simulation', 'operations':{
            'read':{'description':'Read temperature', 'parameters':{}}}}

    def invoke(self, operation, arguments, cancelled):
        # Replace with the vendor SDK and return its observed value.
        return {'value':23.0, 'unit':'degC', 'source':'simulation'}
