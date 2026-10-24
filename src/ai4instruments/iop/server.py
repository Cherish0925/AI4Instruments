"""HTTP interface shared by command-line clients, programs and the local reader."""
from __future__ import annotations
import base64
import hmac
import json
import shutil
import socketserver
import threading
import time
import platform
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .config import VERSION
from .discovery import discover
from .engine import relative_path
from .store import dumps
from .resources import QueueFull
from .errors import RequestError


class RequestBody(dict):
    def __missing__(self, field):
        raise RequestError('missing_field', 'Provide field: ' + field, status=400, field=field)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 256

    def server_bind(self):
        # A local instrument service does not need reverse DNS to start listening.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]

    def __init__(self, address, engine):
        self.engine = engine
        self.started = time.monotonic()
        super().__init__(address, Handler)
        host, port = self.server_address[:2]
        engine.endpoint = f"http://{'127.0.0.1' if host == '0.0.0.0' else host}:{port}"


class Handler(BaseHTTPRequestHandler):
    server_version = "IOP/" + VERSION

    def log_message(self, *_):
        pass

    def _send(self, data, code=200, media_type=None):
        payload = data if isinstance(data, bytes) else dumps(data).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', media_type or 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        self._handle('GET')

    def do_POST(self):
        self._handle('POST')

    def _handle(self, method):
        engine = self.server.engine
        url = urlparse(self.path); parts = url.path.strip('/').split('/')
        query = {k:v[0] for k,v in parse_qs(url.query).items()}
        try:
            if method == 'GET' and url.path == '/':
                return self._send(Path(__file__).with_name('reader.html').read_bytes(), media_type='text/html; charset=utf-8')
            if method == 'GET' and len(parts) == 2 and parts[0] == 'ui' and parts[1] in {
                'app.css', 'app.js', 'core.js', 'devices.js', 'platforms.js', 'runs.js', 'resources.js', 'mark.svg'
            }:
                file = Path(__file__).with_name('ui') / parts[1]
                media = {'.js':'text/javascript; charset=utf-8', '.css':'text/css; charset=utf-8', '.svg':'image/svg+xml'}
                return self._send(file.read_bytes(), media_type=media[file.suffix])
            if method == 'GET' and url.path == '/health':
                return self._send({'service':'IOP', 'version':VERSION})
            expected = 'Bearer ' + engine.config['token']
            if not hmac.compare_digest(self.headers.get('Authorization', ''), expected):
                return self._send({'error':'A service token is required', 'code':'authentication_required'}, 401)
            body = {}
            if method == 'POST':
                length = int(self.headers.get('Content-Length', '0'))
                if len(parts) == 4 and parts[:2] == ['v1', 'runs'] and parts[3] == 'files':
                    return self._send(engine.artifact_stream(parts[2], query['name'], self.rfile, length))
                if len(parts) == 6 and parts[:2] == ['v1', 'runs'] and parts[3] == 'streams' and parts[5] == 'chunks':
                    from .streams import append
                    return self._send(append(engine, parts[2], parts[4], query['sequence'], self.rfile, length))
                if not 0 < length <= 64 * 1024 * 1024:
                    raise ValueError('Request body must be between 1 byte and 64 MiB')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('Expected a JSON object')
                body = RequestBody(body)
            result = None
            if parts == ['v1','status'] and method == 'GET':
                result = {'version':VERSION, 'hostname':platform.node(), 'system':platform.system(),
                          'uptime_s':round(time.monotonic() - self.server.started), **engine.metrics()}
            elif parts == ['v1', 'context'] and method == 'GET':
                from .context import laboratory
                result = laboratory(engine, query.get('refresh') == 'true', query.get('detail', 'summary'))
            elif parts == ['v1', 'context', 'changes'] and method == 'GET':
                from .context import changes
                result = changes(engine, query.get('after', 0), query.get('limit', 100), query.get('wait', 0))
            elif parts == ['v1', 'context', 'devices'] and method == 'GET':
                from .context import device_page
                result = device_page(engine, query.get('offset', 0), query.get('limit', 100))
            elif len(parts) == 3 and parts[:2] == ['v1', 'schemas'] and method == 'GET':
                from .context import schema_document
                result = schema_document(parts[2])
            elif parts == ['v1', 'ui'] and method == 'GET':
                from .desktop import available, has_display
                result = {'desktop_installed':available(), 'desktop_available':available() and has_display(),
                          'local':self.client_address[0] in ('127.0.0.1', '::1')}
            elif parts == ['v1', 'ui', 'desktop'] and method == 'POST':
                if self.client_address[0] not in ('127.0.0.1', '::1'):
                    raise ValueError('Open the desktop application on your computer, then connect it to this service.')
                from .desktop import spawn
                result = spawn(engine.home, body.get('view', 'overview'))
            elif parts == ['v1', 'resources']:
                result = engine.configure_resources(body['capacities']) if method == 'POST' else engine.resource_info()
            elif parts == ['v1', 'adapters'] and method == 'GET':
                from .plugins import adapters
                result = adapters()
            elif parts == ['v1', 'instrument-profiles']:
                result = engine.save_instrument_profile(body) if method == 'POST' else engine.instrument_profiles()
            elif parts == ['v1','platforms']:
                result = engine.apply_platform(body['definition'], body.get('expected_revision', 0)) if method == 'POST' else engine.list_platforms()
            elif parts == ['v1','resources','resolve'] and method == 'POST':
                result = engine.resolve_resources(body['resources'], body['observation'])
            elif parts == ['v1','platforms','preview'] and method == 'POST':
                with engine.lock:
                    result = {'definition': engine.prepare_platform(body['definition'])}
            elif len(parts) == 3 and parts[:2] == ['v1','platforms'] and method == 'GET':
                result = engine.platform_info(parts[2])
            elif len(parts) == 4 and parts[:2] == ['v1','platforms'] and parts[3] == 'history' and method == 'GET':
                result = engine.store.platform_history(parts[2])
            elif len(parts) == 5 and parts[:2] == ['v1','platforms'] and parts[3] == 'procedures' and method == 'POST':
                result = engine.run_procedure(parts[2], parts[4], body.get('request_id'))
            elif parts == ['v1','devices']:
                if method == 'POST':
                    result = engine.register(body)
                else:
                    with engine.lock:
                        result = list(engine.descriptions.values())
            elif parts == ['v1', 'devices', 'batch'] and method == 'POST':
                result = engine.register_many(body['devices'])
            elif len(parts) == 3 and parts[:2] == ['v1','devices'] and method == 'GET':
                with engine.lock:
                    result = dict(engine.descriptions[parts[2]], status=engine.device_states()[parts[2]])
            elif len(parts) == 4 and parts[:2] == ['v1', 'devices'] and parts[3] == 'history' and method == 'GET':
                result = engine.store.device_history(parts[2], query.get('limit', 100))
            elif len(parts) == 4 and parts[:2] == ['v1', 'devices'] and parts[3] == 'configuration' and method == 'POST':
                result = engine.configure_device(parts[2], body['definition'], body['expected_revision'])
            elif len(parts) == 4 and parts[:2] == ['v1', 'devices'] and parts[3] == 'configuration' and method == 'GET':
                with engine.lock:
                    result = engine.device_records[parts[2]]
            elif len(parts) == 4 and parts[:2] == ['v1', 'devices'] and parts[3] == 'reconnect' and method == 'POST':
                result = engine.reconnect(parts[2])
            elif len(parts) == 4 and parts[:2] == ['v1', 'devices'] and parts[3] == 'identify' and method == 'POST':
                result = engine.identify(parts[2], body.get('request_id'))
            elif parts == ['v1', 'discovery', 'retry'] and method == 'POST':
                engine.enrollment.retry(body.get('key'))
                result = engine.request_scan()
            elif parts == ['v1','discovery']:
                result = engine.request_scan() if method == 'POST' else engine.inventory() if query.get('cached') == 'true' else engine.scan()
                result['registered'] = list(engine.descriptions.values())
            elif parts == ['v1','runs']:
                result = engine.submit(body) if method == 'POST' else engine.store.list('runs', limit=int(query.get('limit',100)), summary=query.get('details') == 'false')
            elif parts == ['v1','packages'] and method == 'POST':
                data = base64.b64decode(body.pop('archive'), validate=True)
                result = engine.submit(body, data)
            elif parts == ['v1','events'] and method == 'GET':
                rows = engine.store.events(query.get('after',0), query.get('run_id'), query.get('limit',200), query.get('wait',0))
                result = {'events':rows, 'cursor':rows[-1]['sequence'] if rows else int(query.get('after',0))}
            elif len(parts) == 3 and parts[:2] == ['v1','operations'] and method == 'GET':
                result = engine.store.wait_operation(parts[2], query.get('wait', 0))
            elif len(parts) == 3 and parts[:2] == ['v1','runs'] and method == 'GET':
                result = engine.run_info(parts[2], details=query.get('details', 'true') != 'false')
            elif len(parts) in (5, 6) and parts[:2] == ['v1', 'runs'] and parts[3] == 'streams':
                from .streams import describe, chunks
                if len(parts) == 6 and parts[5] == 'chunks' and method == 'GET':
                    result = chunks(engine, parts[2], parts[4], query.get('after', -1), query.get('limit', 100))
                elif len(parts) == 5:
                    result = describe(engine, parts[2], parts[4], body['definition'] if method == 'POST' else None)
                else:
                    raise KeyError(url.path)
            elif len(parts) == 4 and parts[:2] == ['v1','runs']:
                run_id, action = parts[2:]
                if action == 'operations' and method == 'POST':
                    result = engine.invoke(run_id, body)
                elif action == 'operations' and method == 'GET':
                    result = engine.store.operation_page(run_id, query.get('after', 0), query.get('limit', 200))
                elif action == 'cancel' and method == 'POST':
                    result = engine.cancel(run_id)
                elif action == 'resume' and method == 'POST':
                    result = engine.resume(run_id, body.get('request_id'))
                elif action == 'checkpoints':
                    engine.store.get('runs', run_id)
                    result = engine.checkpoint(run_id, body.get('name', 'main'), body['state']) if method == 'POST' else engine.store.checkpoints(run_id)
                elif action == 'result' and method == 'POST':
                    result = engine.save_result(run_id, body['result'])
                elif action == 'result' and method == 'GET':
                    result = engine.store.get('runs', run_id).get('result')
                elif action == 'artifacts':
                    result = engine.artifact(run_id, body['name'], base64.b64decode(body['data'], validate=True)) if method == 'POST' else engine.store.list('artifacts', run_id, 10000)
                else:
                    raise KeyError(url.path)
            elif len(parts) == 3 and parts[:2] == ['v1','artifacts'] and method == 'GET':
                record = engine.store.get('artifacts', parts[2])
                root = (engine.home / 'runs' / record['run_id']).resolve()
                path = root / relative_path(record['name'])
                if not path.resolve().is_relative_to(root):
                    raise ValueError('File is outside its experiment directory')
                self.send_response(200)
                self.send_header('Content-Type',record['media_type'])
                self.send_header('Content-Length',str(path.stat().st_size))
                self.end_headers()
                with path.open('rb') as file:
                    shutil.copyfileobj(file,self.wfile,256*1024)
                return
            elif parts == ['v1','shutdown'] and method == 'POST':
                self._send({'stopping':True})
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return
            else:
                raise KeyError(url.path)
            self._send(result)
        except RequestError as error:
            self._send(error.response(), error.status)
        except QueueFull as error:
            self._send({'error':str(error), 'code':'queue_full', 'retry_after':1}, 503)
        except KeyError as error:
            self._send({'error':'Not found: ' + str(error), 'code':'not_found'}, 404)
        except (ValueError, TypeError, FileNotFoundError) as error:
            self._send({'error':str(error), 'code':'invalid_request'}, 400)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as error:
            self._send({'error':type(error).__name__ + ': ' + str(error)}, 500)
