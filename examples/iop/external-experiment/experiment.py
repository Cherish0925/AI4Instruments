"""Run against an IOP demo service from this Python environment."""
import json
import uuid
from ai4instruments.iop import Client


client = Client()
run = client.start_experiment(name='External polarization scan', resources=['stage', 'meter'],
                              request_id='scan-' + uuid.uuid4().hex)
print('Experiment:', run.id, flush=True)
try:
    samples, operations = [], []
    for angle in (0, 15, 30, 45):
        run.invoke('stage', 'move_to', {'angle_deg':angle}, request_id=f'{run.id}-move-{angle}')
        measurement = run.invoke_record('meter', 'measure', request_id=f'{run.id}-read-{angle}')
        samples.append({'angle_deg':angle, 'operation_id':measurement['id'], 'measurement':measurement['result']})
        operations.append(measurement['id'])
        run.checkpoint({'next_index':len(samples)})
    run.save_file('measurements.json', json.dumps(samples), operation_ids=operations)
    run.save_result({'points':len(samples)})
    run.finish()
except BaseException:
    run.cancel()
    raise
