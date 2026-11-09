"""Run a continuous scan against an IOP demonstration service."""
import uuid
from ai4instruments.iop import Client

with Client() as client:
    with client.start_experiment(name='External scan', resources=['stage', 'meter'],
                                request_id='scan-' + uuid.uuid4().hex) as run:
        print('Experiment:', run.id, flush=True)
        points = 0
        for angle in (0, 15, 30, 45):
            records = run.batch([
                {'id':'set','device':'stage','operation':'move_to','arguments':{'angle_deg':angle}},
                {'id':'read','device':'meter','operation':'measure'}
            ], request_id=f'{run.id}-point-{angle}')
            measured = records[-1]['result']
            run.save_acquisition(f'point-{angle}.json', [op['id'] for op in records],
                conditions={'requested_angle_deg':angle}, analysis={'power_W':measured['power']})
            points += 1
            run.checkpoint({'next_index':points})
        run.save_result({'points':points})
