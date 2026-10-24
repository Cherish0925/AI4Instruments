"""Continue experiment programs from their explicitly saved progress."""
import copy
import json
import shutil
from .errors import RequestError
from .store import now, dumps


def checkpoint(engine, run_id, name, state):
    from .platforms import name as valid_name
    valid_name(name, 'Progress name')
    state = json.loads(dumps(state))
    with engine.lock:
        run = engine.runs.get(run_id)
        if not run or run['kind'] != 'package' or run['state'] != 'running':
            raise RequestError('program_not_running', 'Save progress from a running experiment program.')
        if engine.remaining[run_id]:
            raise RequestError('operations_pending', 'Wait for the program’s instrument operations before saving progress.')
        return engine.store.save_checkpoint(run_id, name, state)


def resume(engine, run_id, request_id):
    from .engine import TERMINAL
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError('Provide request_id for this continuation')
    with engine.lock:
        run = engine.store.get('runs', run_id)
        if run.get('resume_request_id') == request_id:
            return run
        if engine.stopping or run_id in engine.runs or run['state'] not in TERMINAL - {'completed'}:
            raise RequestError('program_not_stopped', 'Continue an interrupted, failed or cancelled program.')
        if run['kind'] != 'package' or run['package'].get('resume') is not True:
            raise RequestError('resume_not_defined', 'The experiment package must declare resume: true and read its saved progress.')
        checkpoints = engine.store.checkpoints(run_id)
        if not checkpoints:
            raise RequestError('progress_missing', 'This program has not saved a progress point.')
        unresolved = set(run['involved_resources']) & engine.resource_holds.keys()
        if unresolved:
            raise RequestError('device_outcome_unknown', 'Record the affected instrument state before continuing.',
                resources=sorted(unresolved), action='/v1/resources/resolve')
        changed = [name for name, description in run['devices'].items()
                   if ({k: v for k, v in engine.descriptions.get(name, {}).items() if k != 'revision'} !=
                       {k: v for k, v in description.items() if k != 'revision'}) or
                   (name in run.get('device_configurations', {}) and
                    engine.device_records.get(name) != run['device_configurations'][name]) or
                   name in engine.offline or name in engine.reconnecting]
        if changed:
            raise RequestError('instruments_changed', 'Restore the program’s instrument descriptions before continuing.', devices=changed)
        if run.get('platform') and engine.platforms.get(run['platform']['id'], {}).get('definition') != run['platform']['definition']:
            raise RequestError('platform_changed', 'The saved platform has changed since this program started.')
        if len(engine.runs) >= int(engine.config.get('max_active_runs', 10000)):
            from .resources import QueueFull
            raise QueueFull('The service has reached its configured number of active experiments')
        attempt = run.get('attempt', 1)
        directory = engine.home / 'runs' / run_id
        # Each attempt retains its output; saved measurement files stay in the same directory.
        for name in ('stdout.txt', 'stderr.txt'):
            path = directory / name
            if path.is_file():
                target = directory / 'attempts' / str(attempt) / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                engine._file_record(run_id, target, target.relative_to(directory).as_posix())
        previous = run['state']
        run = copy.deepcopy(run)
        for key in ('ended', 'started', 'error', 'end_state', 'exit_code', 'terminate_at'):
            run.pop(key, None)
        run.update(state='queued', attempt=attempt + 1, resume_request_id=request_id,
                   resumed=now(), operations=[], result=None)
        with engine.store.transaction():
            engine.store.put('runs', run)
            engine.store.event('run.resumed', run_id, attempt=run['attempt'], previous_state=previous)
        engine.runs[run_id] = run
        engine._index_run(run)
        engine.wake.set()
        return copy.deepcopy(run)
