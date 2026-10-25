"""Modbus and HTTP instruments using the same operation interface."""
from __future__ import annotations
import json
import math
import threading
from concurrent.futures import CancelledError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from .drivers import Driver
from .store import now


class _ModbusBus:
    def __init__(self, config, transport):
        self.transport = transport
        self.settings = ({k: config.get(k, default) for k, default in
                          (('baudrate', 19200), ('bytesize', 8), ('parity', 'N'), ('stopbits', 1))}
                         if transport == 'serial' else {})
        self.address = config['port'] if transport == 'serial' else config['host']
        self.port = int(config.get('port', 502)) if transport == 'tcp' else None
        self.client = None
        self.owners = set()
        self.lock = threading.RLock()

    def connect(self, timeout):
        if self.client is None:
            from pymodbus.client import ModbusTcpClient, ModbusSerialClient
            options = {'timeout': timeout, 'retries': 0}
            self.client = (ModbusSerialClient(self.address, **self.settings, **options) if self.transport == 'serial'
                           else ModbusTcpClient(self.address, port=self.port, **options))
        self.client.comm_params.timeout_connect = timeout
        if not self.client.connect():
            self.close()
            raise ConnectionError('Could not connect to Modbus bus')
        if self.client.socket is not None:
            if self.transport == 'serial':
                self.client.socket.timeout = self.client.socket.write_timeout = timeout
            else:
                self.client.socket.settimeout(timeout)
        return self.client

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None


class Modbus(Driver):
    def __init__(self, *args):
        super().__init__(*args)
        self.transport = self.config.get('transport', 'tcp')
        if self.transport not in {'tcp', 'serial'}:
            raise ValueError('Modbus transport must be tcp or serial')
        self.unit = self.config.get('device_id', 1)
        minimum, maximum = (1, 247) if self.transport == 'serial' else (0, 255)
        if type(self.unit) is not int or not minimum <= self.unit <= maximum:
            raise ValueError(f'Modbus {self.transport} device_id must be an integer from {minimum} to {maximum}')
        self.timeout = float(self.config.get('timeout', 3))
        if not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('Modbus timeout must be a positive number')
        from .discovery import device_connection
        self.bus = device_connection({'driver': 'modbus', 'config': self.config})
        session = _ModbusBus(self.config, self.transport)
        for other in self.registry.values():
            if isinstance(other, Modbus) and other.bus == self.bus and other._session is not None:
                if other._session.settings != session.settings:
                    raise ValueError('Devices on one Modbus bus must use the same serial settings')
                session = other._session
                break
        self._session = session
        with session.lock:
            session.owners.add(self)

    @property
    def connection(self):
        return self._session.client if self._session else None

    def describe(self):
        address={'type':'integer','minimum':0,'maximum':65535}
        count={'type':'integer','minimum':1,'maximum':125,'default':1}
        device={'type':'integer','enum':[self.unit],'default':self.unit}
        operations={
            'read_holding_registers':{'parameters':{'address':address,'count':count,'device_id':device}},
            'read_input_registers':{'parameters':{'address':address,'count':count,'device_id':device}},
            'read_coils':{'parameters':{'address':address,'count':count,'device_id':device}},
            'read_discrete_inputs':{'parameters':{'address':address,'count':count,'device_id':device}},
            'write_register':{'parameters':{'address':address,'value':{'type':'integer','minimum':0,'maximum':65535},'device_id':device}},
            'write_coil':{'parameters':{'address':address,'value':{'type':'boolean'},'device_id':device}},
            'write_registers':{'parameters':{'address':address,'values':{'type':'array','minItems':1,'maxItems':123,'items':{'type':'integer','minimum':0,'maximum':65535}},'device_id':device}},
        }
        operations.update(self.config.get('operations',{}))
        return {'name':self.config.get('name',self.id),'mode':'hardware','transport':'modbus-'+self.transport,
                'connection':{'bus':self.bus, 'device_id':self.unit},
                'resources':['modbus:'+self.bus], 'operations':operations}

    def connect(self):
        if self._session is None:
            raise ConnectionError('Modbus device is closed')
        with self._session.lock:
            self._session.connect(self.timeout)

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():raise CancelledError()
        spec=self.describe()['operations'][operation]
        function=spec.get('function',operation)
        allowed={'read_holding_registers','read_input_registers','read_coils','read_discrete_inputs','write_register','write_registers','write_coil'}
        if function not in allowed:raise ValueError('Unknown Modbus function: '+function)
        values=dict(spec.get('arguments',{}))
        values.update(arguments)
        if 'value_parameter' in spec:
            value=values.pop(spec['value_parameter'])
            values['value']=round((value-float(spec.get('offset',0)))/float(spec.get('scale',1)))
        values.setdefault('device_id', self.unit)
        if values['device_id'] != self.unit:
            raise ValueError('Use the instrument registered at the requested Modbus address')
        session = self._session
        if session is None:
            raise ConnectionError('Modbus device is closed')
        with session.lock:
            if cancelled.is_set():
                raise CancelledError()
            if self not in session.owners:
                raise ConnectionError('Modbus device is closed')
            try:
                client = session.connect(self.timeout)
                response = getattr(client, function)(**values)
            except Exception:
                # Drop this connection for all users; do not repeat the request.
                session.close()
                raise
        if response.isError():raise RuntimeError(str(response))
        result={'time':now(),'source':'device','function':function}
        if function.startswith('read_'):
            data=list(response.bits[:values.get('count',1)]) if function in {'read_coils','read_discrete_inputs'} else list(response.registers)
            result['values']=data
            if len(data)==1:
                raw=data[0]
                if spec.get('signed') and isinstance(raw,int) and raw>=32768:raw-=65536
                result['value']=raw*float(spec.get('scale',1))+float(spec.get('offset',0))
            if 'unit' in spec:result['unit']=spec['unit']
        else:
            result['acknowledged']=True
        return result

    def close(self):
        session, self._session = self._session, None
        if session is not None:
            with session.lock:
                session.owners.discard(self)
                if not session.owners:
                    session.close()


class HTTP(Driver):
    def describe(self):
        return {'name':self.config.get('name',self.id),'mode':self.config.get('mode', 'hardware'),'transport':'http',
                'concurrency':self.config.get('concurrency', 1), 'requirements':self.config.get('requirements', {}),
                'operations':self.config.get('operations',{})}

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():raise CancelledError()
        spec=self.config['operations'][operation]
        if 'job' in spec:
            from .http_jobs import execute
            return execute(self, spec, arguments, cancelled)
        content = self.request(spec, arguments)
        value=content
        for key in spec.get('result_path',[]):
            value=value[key]
        result={'value':value,'response':content,'time':now(),'source':self.config.get('mode', 'device')}
        if 'unit' in spec:result['unit']=spec['unit']
        return result

    def request(self, spec, arguments):
        def fill(value):
            if isinstance(value,str):
                if value.startswith('${') and value.endswith('}') and value[2:-1] in arguments:
                    return arguments[value[2:-1]]
                return value
            if isinstance(value,dict):return {k:fill(v) for k,v in value.items()}
            if isinstance(value,list):return [fill(v) for v in value]
            return value
        path=spec['path'].format_map({k:quote(str(v),safe='') for k,v in arguments.items()})
        url=self.config['base_url'].rstrip('/')+'/'+path.lstrip('/')
        if spec.get('query'):
            url+='?'+urlencode(fill(spec['query']))
        data=json.dumps(fill(spec['body']),allow_nan=False).encode() if 'body' in spec else None
        headers={'Content-Type':'application/json',**self.config.get('headers',{})}
        request=Request(url,data=data,headers=headers,method=spec.get('method','GET').upper())
        with urlopen(request,timeout=float(self.config.get('timeout',10))) as response:
            payload=response.read()
            content=json.loads(payload) if payload else None
        return content
