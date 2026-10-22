"""Measure local scheduling and SQLite recording, with no instrument I/O."""
import argparse
import json
import os
import platform
import tempfile
import time
from pathlib import Path
from ai4instruments.iop import Driver
from ai4instruments.iop.config import initialize, VERSION
from ai4instruments.iop.engine import Engine, TERMINAL


class Immediate(Driver):
    def describe(self):
        return {'mode':'simulation','operations':{'read':{'parameters':{}}}}

    def invoke(self, operation, arguments, cancelled):
        return {'value':1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, default=5000)
    parser.add_argument('--devices', type=int, default=128)
    parser.add_argument('--workers', type=int, default=64)
    parser.add_argument('--pattern', choices=['serial','parallel'], default='serial')
    parser.add_argument('--output')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='iop-load-') as home:
        config = initialize(home)
        config.update(workers=args.workers, discovery_interval=0)
        config['devices'] = [{'id':'device-' + str(i),'driver':__name__ + ':Immediate'} for i in range(args.devices)]
        engine = Engine(home, config)
        try:
            steps = [{'id':str(i),'device':'device-' + str(i % args.devices),'operation':'read',
                      'after':[str(i-1)] if args.pattern=='serial' and i else []} for i in range(args.steps)]
            begin = time.perf_counter()
            run = engine.submit({'name':'Scheduling measurement','steps':steps})
            accepted = time.perf_counter()
            engine.start()
            while True:
                with engine.lock:
                    active = run['id'] in engine.runs
                if not active:
                    break
                if time.perf_counter()-begin > 180:
                    raise TimeoutError('Scheduling measurement exceeded 180 seconds')
                time.sleep(0.01)
            ended = time.perf_counter()
            record = engine.store.get('runs',run['id'])
            if record['state'] != 'completed' or len(record['result']) != args.steps:
                raise RuntimeError(record.get('error',record['state']))
            result = {'version':VERSION,'system':platform.platform(),'python':platform.python_version(),
                      'cpu_count':os.cpu_count(), 'pattern':args.pattern,'steps':args.steps,'devices':args.devices,
                      'workers':args.workers, 'submission_seconds':round(accepted-begin,4),
                      'execution_seconds':round(ended-accepted,4),
                      'operations_per_second':round(args.steps/(ended-accepted),1),
                      'scope':'Simulated immediate operations with local SQLite recording; not hardware throughput'}
            if args.output:
                Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
            print(json.dumps(result,indent=2))
        finally:
            engine.close()


if __name__ == '__main__':
    main()
