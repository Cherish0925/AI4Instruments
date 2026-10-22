"""Run on the service computer; the processor path must exist on that computer."""
from pathlib import Path
from ai4instruments.iop import Client

lab = Client()
capacities = lab.resources()['capacities']
capacities.setdefault('cpu', 4)
lab.configure_resources(capacities)
if 'processor' not in {device['id'] for device in lab.devices()}:
    lab.register({'id':'processor', 'driver':'command', 'config':{
        'cwd':str(Path(__file__).resolve().parent), 'concurrency':4, 'requirements':{'cpu':1},
        'operations':{'calculate':{'command':['{python}','processor.py'], 'parameters':{
            'values':{'type':'array','minItems':1,'items':{'type':'number'}},
            'scale':{'type':'number','default':1}}}}}})
run = lab.submit([
    {'id':'first','device':'processor','operation':'calculate','arguments':{'values':[1,2,3],'scale':2}},
    {'id':'second','device':'processor','operation':'calculate','arguments':{'scale':3},
     'bindings':{'values':{'step':'first','path':['values']}}},
], name='Array processing')
print(run.id)
print(run.result())
for file in run.files():
    print(file['name'], file['size'])
