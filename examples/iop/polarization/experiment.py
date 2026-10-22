"""Scan through the platform service and retain measurements and analysis."""
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ai4instruments.iop import Client

client = Client()
run = client.current_run()
parameters = json.loads(os.environ.get('IOP_PARAMETERS_JSON', '{}'))
angles = parameters.get('angles_deg', [0, 15, 30, 45, 60, 75, 90])
rows = []
with ThreadPoolExecutor(max_workers=2) as pool:
    for angle in angles:
        move = pool.submit(run.invoke, 'stage', 'move_to', {'angle_deg':angle})
        configure = pool.submit(run.invoke, 'meter', 'configure', {'exposure_s':0.02})
        actual = move.result()['angle_actual']
        configure.result()
        reading = run.invoke('meter', 'measure')
        rows.append({'angle_deg':actual, 'power_W':reading['power'], 'time':reading['time']})
        print(json.dumps(rows[-1]), flush=True)

output = Path(os.environ['IOP_RUN_DIR'])
with (output/'scan.csv').open('w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['angle_deg','power_W','time'])
    writer.writeheader()
    writer.writerows(rows)
best = max(rows, key=lambda x:x['power_W'])
run.save_result({'points':len(rows), 'maximum':best, 'data':'scan.csv'})
