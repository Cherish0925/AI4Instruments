"""Small laboratory models for running domain-independent experiment programs."""
import math
import time
from concurrent.futures import CancelledError
from .drivers import Driver
from .store import now


class Laboratory(Driver):
    def __init__(self,*args):
        super().__init__(*args)
        self.value=float(self.config.get('initial',0))

    def describe(self):
        kind=self.config['kind']
        number=lambda unit,minimum=0: {'type':'number','unit':unit,'minimum':minimum}
        models={
            'temperature':{'set_temperature':{'parameters':{'kelvin':number('K')}},'read_temperature':{'parameters':{}}},
            'balance':{'tare':{'parameters':{}},'read_mass':{'parameters':{}}},
            'pump':{'dispense':{'parameters':{'milliliters':number('mL')}}},
            'daq':{'acquire':{'parameters':{'count':{'type':'integer','minimum':1,'maximum':10000,'default':32},'rate_hz':{'type':'number','minimum':0.1,'default':1000}}}},
        }
        return {'name':self.id,'mode':'simulation','kind':kind,'model':'laboratory-example/1','operations':models[kind]}

    def invoke(self,operation,arguments,cancelled):
        if cancelled.wait(float(self.config.get('latency',0.02))):raise CancelledError()
        result={'time':now(),'source':'simulation'}
        if operation=='set_temperature':
            self.value=arguments['kelvin'];result.update(value=self.value,unit='K')
        elif operation=='read_temperature':result.update(value=self.value,unit='K')
        elif operation=='tare':self.value=0;result.update(value=0,unit='g')
        elif operation=='read_mass':result.update(value=self.value,unit='g')
        elif operation=='dispense':
            amount=arguments['milliliters'];target=self.registry[self.config['balance']]
            target.value+=amount*float(self.config.get('density_g_ml',1))
            result.update(value=amount,unit='mL')
        elif operation=='acquire':
            count=arguments['count'];rate=arguments['rate_hz']
            if cancelled.wait(count/rate):raise CancelledError()
            result.update(values=[math.sin(2*math.pi*i/count) for i in range(count)],unit='V',sample_rate_hz=rate)
        return result
