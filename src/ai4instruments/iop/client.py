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

    def discover(self):
        return self.request('/v1/discovery')

    def register(self, record):
        return self.request('/v1/devices', record)

    def submit(self, steps, *, name='Experiment', project=None, experiment=None, resources=(), request_id=None, parameters=None):
        return Run(self, self.request('/v1/runs', {'name':name, 'project':project, 'experiment':experiment,
                   'steps':steps, 'resources':list(resources), 'parameters':parameters or {},
                   'request_id':request_id or str(uuid.uuid4())})['id'])

    def submit_package(self, path, *, name=None, project=None, experiment=None, resources=(), parameters=None, request_id=None):
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
                           'project':project, 'experiment':experiment, 'resources':list(resources),
                           'parameters':parameters or {}, 'request_id':request_id or str(uuid.uuid4())})
        return Run(self, run['id'])

    def run(self, run_id):
        return Run(self, run_id)

    def current_run(self):
        return Run(self, os.environ['IOP_RUN_ID'])

    def invoke(self, device, operation, arguments=None, timeout=None):
        run = self.submit([{'id':'call', 'device':device, 'operation':operation, 'arguments':arguments or {}}])
        return run.result(timeout)['call']

    def events(self, after=0, run_id=None):
        return self.request('/v1/events?' + urlencode({k:v for k,v in {'after':after,'run_id':run_id}.items() if v is not None}))


class Run:
    def __init__(self, client, run_id):
        self.client, self.id = client, run_id

    def info(self):
        return self.client.request('/v1/runs/'+self.id)

    def wait(self, timeout=None, interval=0.1):
        deadline = time.monotonic() + timeout if timeout is not None else None
        while True:
            info = self.info()
            if info['state'] in TERMINAL:
                return info
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError('Experiment is still running: '+self.id)
            time.sleep(interval)

    def result(self, timeout=None):
        info = self.wait(timeout)
        if info['state'] != 'completed':
            raise IOPError(f"{self.id}: {info['state']}: {info.get('error','')}")
        return info['result']

    def cancel(self):
        return self.client.request('/v1/runs/'+self.id+'/cancel', {})

    def invoke(self, device, operation, arguments=None, timeout=None, request_id=None):
        op = self.client.request('/v1/runs/'+self.id+'/operations', {'device':device, 'operation':operation,
                                 'arguments':arguments or {}, 'request_id':request_id or str(uuid.uuid4())})
        deadline = time.monotonic() + timeout if timeout is not None else None
        while op['state'] not in TERMINAL:
            if deadline is not None and time.monotonic() >= deadline:
                raise TimeoutError('Operation is still running: '+op['id'])
            time.sleep(0.05)
            op = self.client.request('/v1/operations/'+op['id'])
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

    def download(self, artifact_id, destination):
        request = Request(self.client.endpoint+'/v1/artifacts/'+artifact_id, headers={'Authorization':'Bearer '+self.client.token})
        with self.client._open(request, timeout=self.client.timeout) as response, Path(destination).open('wb') as file:
            shutil.copyfileobj(response,file,256*1024)

    def watch(self, after=0, interval=0.2):
        terminal_observed = False
        while True:
            page = self.client.events(after, self.id)
            for event in page['events']:
                yield event
            after = page['cursor']
            # Drain queued events before observing completion.
            if not page['events'] and self.info()['state'] in TERMINAL:
                if terminal_observed:
                    return
                terminal_observed = True
                continue
            if not page['events']:
                time.sleep(interval)


IOP = Client
