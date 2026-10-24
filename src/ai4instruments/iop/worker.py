"""JSON-lines instrument worker; stdout carries replies and stderr carries SDK logs."""
from __future__ import annotations
import json
import sys
import threading
from concurrent.futures import CancelledError
from .drivers import make_driver, parameters


def main():
    output = sys.stdout
    sys.stdout = sys.stderr
    devices = {}
    active = {}
    lock = threading.Lock()
    def reply(value):
        with lock:
            output.write(json.dumps(value, allow_nan=False) + '\n'); output.flush()
    def invoke(message, cancelled):
        try:
            p=message['params'];driver=devices[p['device']]
            args=parameters(driver.describe()['operations'][p['operation']],p.get('arguments',{}))
            result=driver.invoke(p['operation'],args,cancelled)
            reply({'id':message['id'],'result':result})
        except CancelledError:
            reply({'id':message['id'],'cancelled':True})
        except Exception as error:
            reply({'id':message['id'],'error':str(error)})
        finally:
            active.pop(message['id'],None)
    try:
        for line in sys.stdin:
            message=json.loads(line);method=message['method'];p=message.get('params',{})
            try:
                if method=='cancel':
                    event=active.get(p.get('id'))
                    if event:event.set()
                    continue
                if method=='configure':
                    if devices:raise ValueError('Worker is already configured')
                    for record in p.get('devices',[]):
                        if record['driver']=='process':raise ValueError('Nested process drivers are not supported')
                        devices[record['id']]=make_driver(record,devices)
                    reply({'id':message['id'],'result':{'devices':list(devices)}})
                elif method=='describe':
                    reply({'id':message['id'],'result':devices[p['device']].describe()})
                elif method=='instrument_description':
                    driver = devices[p['device']]
                    driver.expected_identity = p['identity']
                    driver.config.update(p['config'])
                    reply({'id':message['id'],'result':driver.describe()})
                elif method=='invoke':
                    from .execution import Context
                    context = p.get('context', {})
                    event = Context(context['run_id'], context['operation_id'], context['output_dir'],
                        lambda value, mid=message['id']: reply({'id':mid,'event':'progress','progress':value})) if context else threading.Event()
                    active[message['id']]=event
                    threading.Thread(target=invoke,args=(message,event),daemon=True).start()
                else:raise ValueError('Unknown worker method: '+method)
            except Exception as error:
                reply({'id':message.get('id'),'error':str(error)})
    finally:
        for event in active.values():event.set()
        for driver in devices.values():driver.close()


if __name__=='__main__':main()
