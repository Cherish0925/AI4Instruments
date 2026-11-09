"""Compare identical immediate operations through three public calling patterns."""
import argparse
import json
import platform
import tempfile
import threading
import time
from pathlib import Path
from ai4instruments.iop import Client
from ai4instruments.iop.config import initialize, VERSION
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server


def measure(pattern, count, size):
    with tempfile.TemporaryDirectory(prefix='iop-calls-') as home:
        config = initialize(home, True, 0)
        config['discovery_interval'] = 0
        engine = Engine(home, config)
        server = Server(('127.0.0.1', 0), engine)
        engine.start()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        client = Client(engine.endpoint, token=config['token'])
        requests = 0
        original = client.request
        def request(*args, **kwargs):
            nonlocal requests
            requests += 1
            return original(*args, **kwargs)
        client.request = request
        try:
            start = time.perf_counter()
            if pattern == 'standalone':
                for _ in range(count):
                    assert client.invoke('stage', 'position')['angle_actual'] == 0
            else:
                with client.start_experiment(resources=['stage']) as run:
                    if pattern == 'continuous':
                        for _ in range(count):
                            assert run.invoke('stage', 'position')['angle_actual'] == 0
                    else:
                        for offset in range(0, count, size):
                            ops = run.batch([{'id':str(i),'device':'stage','operation':'position'}
                                for i in range(offset, min(count, offset + size))])
                            assert all(op['result']['angle_actual'] == 0 for op in ops)
            elapsed = time.perf_counter() - start
            with engine.store.lock:
                runs = engine.store.db.execute('SELECT COUNT(*) FROM runs').fetchone()[0]
                operations = engine.store.db.execute('SELECT COUNT(*) FROM operations').fetchone()[0]
                engine.store.db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            assert operations == count
            return {'pattern':pattern, 'operations':count, 'seconds':round(elapsed, 4),
                    'operations_per_second':round(count / elapsed, 1), 'http_requests':requests,
                    'runs':runs, 'database_bytes':(Path(home)/'records.sqlite3').stat().st_size,
                    'run_files_bytes':sum(p.stat().st_size for p in (Path(home)/'runs').rglob('*') if p.is_file())}
        finally:
            client.close(); server.shutdown(); server.server_close(); engine.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--operations', type=int, default=200)
    parser.add_argument('--batch-size', type=int, default=25)
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.operations < 1 or not 1 <= args.batch_size <= 10000:
        parser.error('Use a positive operation count and a batch size from 1 to 10000')
    result = {'version':VERSION, 'system':platform.platform(), 'python':platform.python_version(),
              'batch_size':args.batch_size, 'results':[measure(p, args.operations, args.batch_size)
                  for p in ('standalone','continuous','batch')],
              'scope':'Same immediate simulated position reads, sequential, local HTTP and SQLite FULL. All three patterns use this source version. No physical instrument timing.'}
    text = json.dumps(result, indent=2) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text)


if __name__ == '__main__':
    main()
