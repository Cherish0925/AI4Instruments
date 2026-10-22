"""HTTP interface shared by command-line clients, programs and the local reader."""
from __future__ import annotations
import base64
import hmac
import json
import shutil
import socketserver
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .config import VERSION
from .discovery import discover
from .engine import relative_path
from .store import dumps


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self):
        # A local instrument service does not need reverse DNS to start listening.
        socketserver.TCPServer.server_bind(self)
        self.server_name, self.server_port = self.server_address[:2]

    def __init__(self, address, engine):
        self.engine = engine
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
            if method == 'GET' and url.path == '/platform.js':
                return self._send(Path(__file__).with_name('platform.js').read_bytes(), media_type='text/javascript; charset=utf-8')
            if method == 'GET' and url.path == '/health':
                return self._send({'service':'IOP', 'version':VERSION})
            expected = 'Bearer ' + engine.config['token']
            if not hmac.compare_digest(self.headers.get('Authorization', ''), expected):
                return self._send({'error':'A service token is required'}, 401)
            body = {}
            if method == 'POST':
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 64 * 1024 * 1024:
                    raise ValueError('Request body must be between 1 byte and 64 MiB')
                body = json.loads(self.rfile.read(length))
                if not isinstance(body, dict):
                    raise ValueError('Expected a JSON object')
            result = None
            if parts == ['v1','status'] and method == 'GET':
                result = {'version':VERSION, **engine.metrics()}
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
            elif len(parts) == 3 and parts[:2] == ['v1','devices'] and method == 'GET':
                result = engine.descriptions[parts[2]]
            elif parts == ['v1','discovery'] and method == 'GET':
                result = engine.scan()
                result['registered'] = list(engine.descriptions.values())
            elif parts == ['v1','runs']:
                result = engine.submit(body) if method == 'POST' else engine.store.list('runs', limit=int(query.get('limit',100)))
            elif parts == ['v1','packages'] and method == 'POST':
                data = base64.b64decode(body.pop('archive'), validate=True)
                result = engine.submit(body, data)
            elif parts == ['v1','events'] and method == 'GET':
                rows = engine.store.events(query.get('after',0), query.get('run_id'), query.get('limit',200))
                result = {'events':rows, 'cursor':rows[-1]['sequence'] if rows else int(query.get('after',0))}
            elif len(parts) == 3 and parts[:2] == ['v1','operations'] and method == 'GET':
                result = engine.store.get('operations', parts[2])
            elif len(parts) == 3 and parts[:2] == ['v1','runs'] and method == 'GET':
                result = engine.store.get('runs', parts[2])
                result['operation_records'] = list(reversed(engine.store.list('operations', parts[2], 10000)))
            elif len(parts) == 4 and parts[:2] == ['v1','runs']:
                run_id, action = parts[2:]
                if action == 'operations' and method == 'POST':
                    result = engine.invoke(run_id, body)
                elif action == 'cancel' and method == 'POST':
                    result = engine.cancel(run_id)
                elif action == 'result' and method == 'POST':
                    result = engine.save_result(run_id, body['result'])
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
        except KeyError as error:
            self._send({'error':'Not found: ' + str(error)}, 404)
        except (ValueError, TypeError, FileNotFoundError) as error:
            self._send({'error':str(error)}, 400)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as error:
            self._send({'error':type(error).__name__ + ': ' + str(error)}, 500)
