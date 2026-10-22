"""Concurrent preparation, measured dosing and acquisition in one hosted program."""
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ai4instruments.iop import Client

run=Client().current_run()
p=json.loads(os.environ['IOP_PARAMETERS_JSON'])
target=float(p.get('target_mass_g',2.5))
if not 0<target<=100:raise ValueError('target_mass_g must be between 0 and 100')
rows=[]
with ThreadPoolExecutor(max_workers=3) as pool:
    heat=pool.submit(run.invoke,'bath','set_temperature',{'kelvin':p.get('temperature_K',298.15)})
    tare=pool.submit(run.invoke,'balance','tare')
    reference=pool.submit(run.invoke,'daq','acquire',{'count':32,'rate_hz':1000})
    heat.result();tare.result();reference.result()
    for point in range(100):
        mass=run.invoke('balance','read_mass')['value']
        if abs(target-mass)<=0.01:break
        # Density is an experiment parameter; feedback uses measured mass.
        volume=min(max((target-mass)/float(p.get('density_g_ml',1)),0),1)
        if volume<=0:raise ValueError('Measured mass exceeds requested mass')
        run.invoke('pump','dispense',{'milliliters':volume})
        t=pool.submit(run.invoke,'bath','read_temperature')
        signal=pool.submit(run.invoke,'daq','acquire',{'count':64,'rate_hz':1000})
        m=pool.submit(run.invoke,'balance','read_mass')
        row={'step':point,'mass_g':m.result()['value'],'temperature_K':t.result()['value'],
             'mean_voltage_V':sum(signal.result()['values'])/64}
        rows.append(row);print(json.dumps(row),flush=True)
    else:raise RuntimeError('Requested mass was not reached in 100 steps')
output=Path(os.environ['IOP_RUN_DIR'])
with (output/'measurements.csv').open('w',newline='',encoding='utf-8') as file:
    writer=csv.DictWriter(file,fieldnames=['step','mass_g','temperature_K','mean_voltage_V'])
    writer.writeheader();writer.writerows(rows)
run.save_result({'target_mass_g':target,'final_mass_g':mass,'steps':len(rows),'data':'measurements.csv'})
