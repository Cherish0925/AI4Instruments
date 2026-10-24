"""Measure sequential SDK calls to immediate simulated operations over local HTTP."""
import argparse
import json
import os
import platform
import tempfile
import threading
import time
from pathlib import Path
from ai4instruments.iop import Client, Driver
from ai4instruments.iop.config import initialize, VERSION
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server


class Immediate(Driver):
    def describe(self):
        return {'mode': 'simulation', 'operations': {'read': {'parameters': {}}}}

    def invoke(self, operation, arguments, cancelled):
        return {'value': 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, default=200)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='iop-program-measurement-') as home:
        config = initialize(home, port=0)
        config.update(discovery_interval=0, devices=[{'id': 'reader', 'driver': __name__ + ':Immediate'}])
        engine = Engine(home, config)
        server = Server(('127.0.0.1', 0), engine)
        engine.start()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        source = Path(home) / 'source'
        source.mkdir()
        (source / 'package.json').write_text(json.dumps({'command': ['{python}', 'experiment.py']}))
        (source / 'experiment.py').write_text(
            'import time\nfrom ai4instruments.iop import Client\nr=Client().current_run()\n'
            f'n={args.steps}\nstart=time.perf_counter()\n'
            'for _ in range(n):\n assert r.invoke("reader","read")["value"]==1\n'
            'r.save_result({"steps":n,"seconds":time.perf_counter()-start})\n')
        try:
            result = Client(engine.endpoint, token=config['token']).submit_package(source).result(180)
            print(json.dumps({'version': VERSION, 'system': platform.platform(), 'python': platform.python_version(),
                              'cpu_count': os.cpu_count(), 'pattern': 'sequential-program', 'steps': args.steps,
                              'execution_seconds': result['seconds'], 'operations_per_second': args.steps / result['seconds'],
                              'scope': 'Immediate simulated operations via Python SDK and local HTTP, including SQLite recording; not instrument throughput'}, indent=2))
        finally:
            server.shutdown()
            server.server_close()
            engine.close()


if __name__ == '__main__':
    main()
