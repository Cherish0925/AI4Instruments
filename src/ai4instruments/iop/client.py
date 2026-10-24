"""IOP Python client. Experiments and devices live in the service."""
from __future__ import annotations
import base64
import io
import json
import os
import shutil
import time
import uuid
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen, build_opener, ProxyHandler
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from .config import home_path
from .engine import TERMINAL


class IOPError(RuntimeError):
    pass


class Client:
    def __init__(self, endpoint=None, token=None, home=None, timeout=30):
        config = {}
        path = home_path(home) / 'config.json'
        if path.exists():
            config = json.loads(path.read_text(encoding='utf-8'))
        host = config.get('host','127.0.0.1')
        self.endpoint = (endpoint or os.environ.get('IOP_ENDPOINT') or f"http://{'127.0.0.1' if host == '0.0.0.0' else host}:{config.get('port',8765)}").rstrip('/')
        self.token = token if token is not None else os.environ.get('IOP_TOKEN', config.get('token',''))
        self.timeout = timeout
        # Loopback instrument services communicate directly, independent of OS proxy settings.
        self._open = build_opener(ProxyHandler({})).open if urlparse(self.endpoint).hostname in {'127.0.0.1','localhost','::1'} else urlopen

    @classmethod
    def connect(cls, endpoint=None, **kwargs):
        return cls(endpoint, **kwargs)

    def request(self, path, body=None, binary=False):
        data = json.dumps(body, allow_nan=False).encode() if body is not None else None
        request = Request(self.endpoint + path, data=data, headers={'Authorization':'Bearer '+self.token,
                          'Content-Type':'application/json'})
        try:
            with self._open(request, timeout=self.timeout) as response:
                data = response.read()
                return data if binary else json.loads(data)
        except HTTPError as error:
            try:
                message = json.loads(error.read()).get('error', str(error))
            except Exception:
                message = str(error)
            raise IOPError(message) from None

    def devices(self):
        return self.request('/v1/devices')

    def context(self, refresh=False):
        return self.request('/v1/context' + ('?refresh=true' if refresh else ''))

    def schema(self, name):
        from urllib.parse import quote
        return self.request('/v1/schemas/' + quote(name, safe=''))

    def discover(self):
        return self.request('/v1/discovery')

    def start_discovery(self):
        return self.request('/v1/discovery', {})

    def inventory(self):
        return self.request('/v1/discovery?cached=true')

    def instrument_profiles(self):
        return self.request('/v1/instrument-profiles')

    def save_instrument_profile(self, profile):
        return self.request('/v1/instrument-profiles', profile)

    def identify(self, device, request_id=None):
        from urllib.parse import quote
        return Run(self, self.request('/v1/devices/' + quote(device, safe='') + '/identify',
                                     {'request_id':request_id or str(uuid.uuid4())})['id'])

    def retry_discovery(self, key=None):
        return self.request('/v1/discovery/retry', {'key':key})

    def register(self, record):
        return self.request('/v1/devices', record)

    def register_many(self, records):
        return self.request('/v1/devices/batch', {'devices': records})

    def reconnect(self, device):
        return self.request('/v1/devices/' + device + '/reconnect', {})

    def adapters(self):
        return self.request('/v1/adapters')

    def resources(self):
        return self.request('/v1/resources')

    def configure_resources(self, capacities):
        return self.request('/v1/resources', {'capacities': capacities})

    def platforms(self):
        return self.request('/v1/platforms')

    def platform(self, platform_id):
        return self.request('/v1/platforms/' + platform_id)

    def configure_platform(self, definition, expected_revision=0):
        return self.request('/v1/platforms', {'definition': definition, 'expected_revision': expected_revision})

    def procedure(self, platform_id, procedure='initialize', request_id=None):
        record = self.request('/v1/platforms/' + platform_id + '/procedures/' + procedure,
                              {'request_id': request_id or str(uuid.uuid4())})
        return Run(self, record['id'])

    def submit(self, steps, *, name='Experiment', project=None, experiment=None, resources=(), request_id=None, parameters=None, platform=None, requirements=None):
        return Run(self, self.request('/v1/runs', {'name':name, 'project':project, 'experiment':experiment,
                   'steps':steps, 'resources':list(resources), 'parameters':parameters or {}, 'platform': platform,
                   'requirements':requirements or {}, 'request_id':request_id or str(uuid.uuid4())})['id'])

    def submit_package(self, path, *, name=None, project=None, experiment=None, resources=(), parameters=None, request_id=None, platform=None, requirements=None):
        path = Path(path)
        if path.is_dir():
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
                for file in sorted(path.rglob('*')):
                    rel = file.relative_to(path)
                    if file.is_file() and not file.is_symlink() and not any(p in {'.git','.venv','venv','__pycache__'} for p in rel.parts):
                        archive.write(file, rel.as_posix())
            data = buffer.getvalue()
        else:
            data = path.read_bytes()
        run = self.request('/v1/packages', {'archive':base64.b64encode(data).decode(), 'name':name or path.stem,
                           'project':project, 'experiment':experiment, 'resources':list(resources), 'platform':platform,
                           'parameters':parameters or {}, 'requirements':requirements or {}, 'request_id':request_id or str(uuid.uuid4())})
        return Run(self, run['id'])

    def run(self, run_id):
        return Run(self, run_id)

    def current_run(self):
        return Run(self, os.environ['IOP_RUN_ID'])

    def invoke(self, device, operation, arguments=None, timeout=None):
        run = self.submit([{'id':'call', 'device':device, 'operation':operation, 'arguments':arguments or {}}])
        return run.result(timeout)['call']

    def events(self, after=0, run_id=None, wait=0):
        return self.request('/v1/events?' + urlencode({k:v for k,v in {'after':after,'run_id':run_id,'wait':wait}.items() if v is not None}))


class Run:
    def __init__(self, client, run_id):
        self.client, self.id = client, run_id

    def info(self, details=True):
        return self.client.request('/v1/runs/'+self.id + ('' if details else '?details=false'))

    def wait(self, timeout=None, interval=0.1, details=True):
        deadline = time.monotonic() + timeout if timeout is not None else None
        cursor = 0
        while True:
            info = self.info(details=False)
            if info['state'] in TERMINAL:
                return self.info() if details else info
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError('Experiment is still running: '+self.id)
            remaining = max(0, deadline - time.monotonic()) if deadline is not None else 25
            page = self.client.events(cursor, self.id, wait=min(25, max(0, self.client.timeout - 1), remaining))
            cursor = page['cursor']
            if self.client.timeout <= 1 and not page['events']:
                time.sleep(min(interval, remaining))

    def result(self, timeout=None):
        info = self.wait(timeout, details=False)
        if info['state'] != 'completed':
            raise IOPError(f"{self.id}: {info['state']}: {info.get('error','')}")
        return self.client.request('/v1/runs/' + self.id + '/result')

    def cancel(self):
        return self.client.request('/v1/runs/'+self.id+'/cancel', {})

    def invoke(self, device, operation, arguments=None, timeout=None, request_id=None):
        op = self.client.request('/v1/runs/'+self.id+'/operations', {'device':device, 'operation':operation,
                                 'arguments':arguments or {}, 'request_id':request_id or str(uuid.uuid4())})
        deadline = time.monotonic() + timeout if timeout is not None else None
        while op['state'] not in TERMINAL:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError('Operation is still running: '+op['id'])
            remaining = max(0, deadline - time.monotonic()) if deadline is not None else 25
            wait = min(25, max(0, self.client.timeout - 1), remaining)
            op = self.client.request('/v1/operations/' + op['id'] + '?' + urlencode({'wait': wait}))
        if op['state'] != 'completed':
            raise IOPError(op.get('error', op['state']))
        return op['result']

    def save_result(self, result):
        return self.client.request('/v1/runs/'+self.id+'/result', {'result':result})

    def save_file(self, name, content):
        data = content.encode() if isinstance(content, str) else content
        return self.client.request('/v1/runs/'+self.id+'/artifacts', {'name':name, 'data':base64.b64encode(data).decode()})

    def files(self):
        return self.client.request('/v1/runs/'+self.id+'/artifacts')

    def operations(self, after=0, limit=200):
        return self.client.request('/v1/runs/' + self.id + '/operations?' + urlencode({'after':after,'limit':limit}))

    def upload(self, source, name=None):
        source = Path(source)
        with source.open('rb') as file:
            data = iter(lambda: file.read(256 * 1024), b'')
            request = Request(self.client.endpoint + '/v1/runs/' + self.id + '/files?' + urlencode({'name':name or source.name}),
                data=data, headers={'Authorization':'Bearer ' + self.client.token,
                                    'Content-Type':'application/octet-stream', 'Content-Length':str(os.fstat(file.fileno()).st_size)})
            with self.client._open(request, timeout=self.client.timeout) as response:
                return json.loads(response.read())

    def download(self, artifact_id, destination):
        request = Request(self.client.endpoint+'/v1/artifacts/'+artifact_id, headers={'Authorization':'Bearer '+self.client.token})
        with self.client._open(request, timeout=self.client.timeout) as response, Path(destination).open('wb') as file:
            shutil.copyfileobj(response,file,256*1024)

    def watch(self, after=0, interval=0.2):
        terminal_observed = False
        while True:
            page = self.client.events(after, self.id, wait=min(25, max(0, self.client.timeout - 1)))
            for event in page['events']:
                yield event
            after = page['cursor']
            # Drain queued events before observing completion.
            if not page['events'] and self.info(details=False)['state'] in TERMINAL:
                if terminal_observed:
                    return
                terminal_observed = True
                continue
            if not page['events']:
                time.sleep(interval)


IOP = Client
