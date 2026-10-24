"""Install, run and use the IOP service."""
from __future__ import annotations
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from .client import Client
from .config import VERSION, InstanceLock, home_path, initialize


def output(value):
    print(json.dumps(value, ensure_ascii=False, indent=2) if not isinstance(value, str) else value)


def serve(home):
    from .engine import Engine
    from .server import Server
    config = initialize(home)
    lock = InstanceLock(home)
    engine = server = None
    try:
        engine = Engine(home, config)
        server = Server((config['host'], int(config['port'])), engine)
        engine.start()
        def halt(*_):
            threading.Thread(target=server.shutdown, daemon=True).start()
        for name in ('SIGTERM','SIGINT'):
            signal.signal(getattr(signal,name), halt)
        print(f'IOP {VERSION}  {engine.endpoint}\nData: {home}', flush=True)
        server.serve_forever(poll_interval=0.1)
    finally:
        if server:
            server.server_close()
        if engine:
            engine.close()
        lock.close()


def start(home):
    config = initialize(home)
    host = '127.0.0.1' if config['host'] == '0.0.0.0' else config['host']
    client = Client(f"http://{host}:{config['port']}", token=config['token'], home=home, timeout=0.5)
    try:
        client.request('/v1/status')
        return 'IOP is already running: ' + client.endpoint
    except Exception:
        pass
    with open(home/'service.log','ab') as log:
        options = {'creationflags':subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP} if sys.platform == 'win32' else {'start_new_session':True}
        process = subprocess.Popen([sys.executable,'-m','ai4instruments.iop','--home',str(home),'serve'],
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=log, **options)
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            client.request('/v1/status')
            return 'IOP is running: '+client.endpoint
        except Exception:
            time.sleep(0.1)
    if process.poll() is not None:
        raise RuntimeError('IOP did not start. Read '+str(home/'service.log'))
    raise RuntimeError('Startup is still pending. Read '+str(home/'service.log'))


def parser():
    root = argparse.ArgumentParser(prog='iop', description='Persistent instrument and experiment service')
    root.add_argument('--version', action='version', version=VERSION)
    root.add_argument('--home', help='Service data directory')
    root.add_argument('--endpoint', help='Remote service URL')
    sub = root.add_subparsers(dest='command', required=True)
    p = sub.add_parser('init', help='Create a configuration'); p.add_argument('--demo', action='store_true'); p.add_argument('--port', type=int, default=8765)
    for name in ['start','serve','stop','status','open','devices','discover','adapters']:
        sub.add_parser(name)
    p = sub.add_parser('desktop', help='Open the native desktop window'); p.add_argument('--view', default='overview')
    sub.add_parser('shortcuts', help='Install desktop and browser application entries')
    p = sub.add_parser('context', help='Read the laboratory configuration for an agent or program')
    p.add_argument('--refresh', action='store_true'); p.add_argument('--start', action='store_true')
    sub.add_parser('mcp', help='Expose the shared service to an agent over MCP stdio')
    sub.add_parser('mcp-config', help='Print the MCP launcher configuration for this installation')
    p = sub.add_parser('register'); p.add_argument('file')
    p = sub.add_parser('reconnect'); p.add_argument('device')
    p = sub.add_parser('identify', help='Read and save instrument identity'); p.add_argument('device'); p.add_argument('--wait', action='store_true')
    p = sub.add_parser('instrument-profile', help='List or save model-specific operations'); p.add_argument('file', nargs='?')
    p = sub.add_parser('resources'); p.add_argument('--set', dest='capacities', help='JSON object of resource capacities')
    p = sub.add_parser('run'); p.add_argument('file'); p.add_argument('--wait', action='store_true')
    p = sub.add_parser('package'); p.add_argument('path'); p.add_argument('--resources', nargs='*', default=[]); p.add_argument('--requirements', default='{}'); p.add_argument('--parameters', default='{}'); p.add_argument('--project'); p.add_argument('--platform'); p.add_argument('--wait', action='store_true')
    p = sub.add_parser('platform', help='Configure and initialize experimental platforms')
    ps = p.add_subparsers(dest='platform_action', required=True)
    ps.add_parser('list')
    for action in ('show', 'history'):
        q = ps.add_parser(action); q.add_argument('id')
    q = ps.add_parser('draft'); q.add_argument('id'); q.add_argument('--devices', nargs='+', required=True); q.add_argument('--output')
    for action in ('preview', 'apply'):
        q = ps.add_parser(action); q.add_argument('file'); q.add_argument('--revision', type=int, default=0)
    for action in ('initialize', 'run'):
        q = ps.add_parser(action); q.add_argument('id'); q.add_argument('--wait', action='store_true')
        if action == 'run': q.add_argument('procedure')
    p = sub.add_parser('call'); p.add_argument('device'); p.add_argument('operation'); p.add_argument('--arguments', default='{}')
    p = sub.add_parser('runs'); p.add_argument('--limit',type=int,default=20)
    for name in ['result','cancel','files']:
        p = sub.add_parser(name); p.add_argument('run_id')
    p = sub.add_parser('events'); p.add_argument('--run-id'); p.add_argument('--after',type=int,default=0)
    p = sub.add_parser('service'); p.add_argument('action',choices=['install','uninstall'])
    return root


def main():
    args = parser().parse_args()
    home = home_path(args.home)
    client = Client(args.endpoint, home=home)
    try:
        if args.command == 'init':
            initialize(home, args.demo, args.port)
            output('Configuration: '+str(home/'config.json'))
        elif args.command == 'serve':
            serve(home)
        elif args.command == 'start':
            output(start(home))
        elif args.command == 'stop':
            output(client.request('/v1/shutdown', {}))
        elif args.command == 'status':
            output(client.request('/v1/status'))
        elif args.command == 'context':
            if args.start:
                from .desktop import ensure_service
                client = ensure_service(home, args.endpoint)
            output(client.context(args.refresh))
        elif args.command == 'mcp-config':
            from .context import agent_configuration
            output(agent_configuration(home, args.endpoint or os.environ.get('IOP_ENDPOINT')))
        elif args.command == 'mcp':
            from .mcp import run
            run(home, args.endpoint)
        elif args.command == 'open':
            from .desktop import open_browser
            open_browser(home, args.endpoint)
        elif args.command == 'desktop':
            from .desktop import launch
            launch(home, args.endpoint, args.view)
        elif args.command == 'shortcuts':
            from .desktop import install_launchers
            output(install_launchers(home))
        elif args.command == 'devices':
            output(client.devices())
        elif args.command == 'discover':
            output(client.discover())
        elif args.command == 'adapters':
            output(client.adapters())
        elif args.command == 'reconnect':
            output(client.reconnect(args.device))
        elif args.command == 'identify':
            run = client.identify(args.device)
            output(run.result() if args.wait else {'run_id': run.id})
        elif args.command == 'instrument-profile':
            output(client.save_instrument_profile(json.loads(Path(args.file).read_text(encoding='utf-8'))) if args.file else client.instrument_profiles())
        elif args.command == 'resources':
            output(client.configure_resources(json.loads(args.capacities)) if args.capacities is not None else client.resources())
        elif args.command == 'register':
            records = json.loads(Path(args.file).read_text(encoding='utf-8'))
            output(client.register_many(records) if isinstance(records,list) else client.register(records))
        elif args.command == 'run':
            spec = json.loads(Path(args.file).read_text(encoding='utf-8'))
            run = client.run(client.request('/v1/runs', spec)['id'])
            output(run.result() if args.wait else {'run_id':run.id})
        elif args.command == 'package':
            run = client.submit_package(args.path, resources=args.resources, parameters=json.loads(args.parameters), project=args.project, platform=args.platform, requirements=json.loads(args.requirements))
            output(run.result() if args.wait else {'run_id':run.id})
        elif args.command == 'platform':
            action = args.platform_action
            if action == 'list': output(client.platforms())
            elif action == 'show': output(client.platform(args.id))
            elif action == 'history': output(client.request('/v1/platforms/' + args.id + '/history'))
            elif action == 'draft':
                from .platforms import description
                draft = description({'schema_version':1, 'id':args.id, 'name':args.id, 'devices':args.devices},
                                    {d['id']:d for d in client.devices()})
                if args.output:
                    from .config import save_json
                    destination = Path(args.output)
                    if destination.exists(): raise ValueError('Choose a new output filename: ' + str(destination))
                    save_json(destination, draft); output(str(destination))
                else: output(draft)
            elif action in ('preview', 'apply'):
                definition = json.loads(Path(args.file).read_text(encoding='utf-8'))
                output(client.request('/v1/platforms/preview', {'definition':definition}) if action == 'preview'
                       else client.configure_platform(definition, args.revision))
            else:
                run = client.procedure(args.id, 'initialize' if action == 'initialize' else args.procedure)
                output(run.result() if args.wait else {'run_id':run.id})
        elif args.command == 'call':
            output(client.invoke(args.device, args.operation, json.loads(args.arguments)))
        elif args.command == 'runs':
            output(client.request('/v1/runs?limit='+str(args.limit)))
        elif args.command == 'result':
            output(client.run(args.run_id).info())
        elif args.command == 'cancel':
            output(client.run(args.run_id).cancel())
        elif args.command == 'files':
            output(client.run(args.run_id).files())
        elif args.command == 'events':
            output(client.events(args.after,args.run_id))
        elif args.command == 'service':
            from . import services
            output(services.install(home) if args.action == 'install' else services.uninstall())
    except (Exception, KeyboardInterrupt) as error:
        print(str(error) or 'Stopped', file=sys.stderr)
        raise SystemExit(1) from None
