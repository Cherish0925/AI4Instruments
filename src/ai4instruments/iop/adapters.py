"""Modbus and HTTP instruments using the same operation interface."""
from __future__ import annotations
import json
from concurrent.futures import CancelledError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen
from .drivers import Driver
from .store import now


class Modbus(Driver):
    def __init__(self, *args):
        super().__init__(*args)
        self.connection = None
        self.transport = self.config.get('transport','tcp')
        if self.transport not in {'tcp','serial'}:
            raise ValueError('Modbus transport must be tcp or serial')
        self.bus = ('serial',self.config['port']) if self.transport=='serial' else ('tcp',self.config['host'],self.config.get('port',502))

    def describe(self):
        address={'type':'integer','minimum':0,'maximum':65535}
        count={'type':'integer','minimum':1,'maximum':125,'default':1}
        device={'type':'integer','minimum':1,'maximum':247,'default':self.config.get('device_id',1)}
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
                'resources':['modbus:'+':'.join(map(str,self.bus))], 'operations':operations}

    def connect(self):
        if self.connection is not None:
            return
        # Logical devices on one serial bus share the same open connection.
        for other in self.registry.values():
            if isinstance(other,Modbus) and other is not self and other.bus==self.bus and other.connection is not None:
                self.connection=other.connection
                return
        from pymodbus.client import ModbusTcpClient, ModbusSerialClient
        options={'timeout':float(self.config.get('timeout',3)),'retries':0}
        if self.transport=='tcp':
            self.connection=ModbusTcpClient(self.config['host'],port=int(self.config.get('port',502)),**options)
        else:
            self.connection=ModbusSerialClient(self.config['port'],baudrate=int(self.config.get('baudrate',19200)),
                parity=self.config.get('parity','N'),stopbits=int(self.config.get('stopbits',1)),**options)
        if not self.connection.connect():
            raise ConnectionError('Could not connect to Modbus device')

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():raise CancelledError()
        self.connect()
        spec=self.describe()['operations'][operation]
        function=spec.get('function',operation)
        allowed={'read_holding_registers','read_input_registers','read_coils','read_discrete_inputs','write_register','write_registers','write_coil'}
        if function not in allowed:raise ValueError('Unknown Modbus function: '+function)
        values=dict(spec.get('arguments',{}))
        values.update(arguments)
        if 'value_parameter' in spec:
            value=values.pop(spec['value_parameter'])
            values['value']=round((value-float(spec.get('offset',0)))/float(spec.get('scale',1)))
        values.setdefault('device_id',self.config.get('device_id',1))
        response=getattr(self.connection,function)(**values)
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
        if self.connection is not None:
            self.connection.close()
            self.connection=None


class HTTP(Driver):
    def describe(self):
        return {'name':self.config.get('name',self.id),'mode':'hardware','transport':'http',
                'operations':self.config.get('operations',{})}

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():raise CancelledError()
        spec=self.config['operations'][operation]
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
        value=content
        for key in spec.get('result_path',[]):
            value=value[key]
        result={'value':value,'response':content,'time':now(),'source':'device'}
        if 'unit' in spec:result['unit']=spec['unit']
        return result
