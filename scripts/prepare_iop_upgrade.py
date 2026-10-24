"""Stop an idle installation before replacing its Python environment."""
import json
import sys
import time
from urllib.error import URLError
from ai4instruments.iop.client import Client
from ai4instruments.iop.config import home_path, InstanceLock

home = home_path(None)
path = home / 'config.json'
if not path.exists():
    sys.exit(0)
config = json.loads(path.read_text(encoding='utf-8'))
host = config.get('host', '127.0.0.1')
client = Client(f"http://{'127.0.0.1' if host == '0.0.0.0' else host}:{config.get('port',8765)}", token=config['token'], timeout=2)
try:
    status = client.request('/v1/status')
except (URLError, ConnectionError, TimeoutError):
    sys.exit(0)
if status.get('active_runs') or status.get('queued_runs'):
    sys.exit('Finish or stop the accepted experiments before upgrading IOP.')
client.request('/v1/shutdown', {})
for _ in range(300):
    try:
        lock = InstanceLock(home)
    except (OSError, RuntimeError):
        time.sleep(0.1)
    else:
        lock.close()
        break
else:
    sys.exit('The previous service is still closing. Install again after it has stopped.')
