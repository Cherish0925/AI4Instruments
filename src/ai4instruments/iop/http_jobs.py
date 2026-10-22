"""Follow remote asynchronous jobs until their service confirms an outcome."""
import math
import time
from concurrent.futures import CancelledError
from .process_driver import DriverUnavailable
from .store import now


def select(value, path):
    for key in path:
        value = value[key]
    return value


def execute(driver, spec, arguments, cancelled):
    job = spec['job']
    interval = float(job.get('poll_interval', 1))
    timeout = float(job.get('timeout', 0))
    if not math.isfinite(interval) or not 0.01 <= interval <= 60 or not math.isfinite(timeout) or timeout < 0:
        raise ValueError('Job polling interval must be 0.01–60 seconds; timeout must be nonnegative')
    # Read the description before submitting anything to the remote service.
    status = job['status']
    state_path = job.get('state_path', ['state'])
    if not isinstance(status, dict) or 'path' not in status:
        raise ValueError('Remote job needs a status request')
    started = time.monotonic()
    identifier = None
    try:
        submitted = driver.request(spec, arguments)
        identifier = select(submitted, job.get('id_path', ['id']))
        values = {**arguments, 'job_id': identifier}
        sent_cancel = False
        while True:
            response = driver.request(status, values)
            state = select(response, state_path)
            if state in job.get('completed', ['completed']):
                return {'value': select(response, job.get('result_path', ['result'])),
                        'job_id': identifier, 'time': now(), 'source': driver.config.get('mode', 'software')}
            if state in job.get('failed', ['failed']):
                raise RemoteFailure('Remote job failed: ' + str(identifier) + ': ' + str(response))
            if state in job.get('cancelled', ['cancelled']):
                raise CancelledError()
            if cancelled.is_set() and not sent_cancel:
                if 'cancel' not in job:
                    raise DriverUnavailable('Remote job does not offer cancellation; inspect job ' + str(identifier))
                driver.request(job['cancel'], values)
                sent_cancel = True
            if hasattr(cancelled, 'progress'):
                fraction = select(response, job['progress_path']) if 'progress_path' in job else None
                cancelled.progress(fraction, str(state), remote_job_id=identifier)
            if timeout and time.monotonic() - started >= timeout:
                raise DriverUnavailable('Remote job is still active after its configured duration: ' + str(identifier))
            # The cancellation request is acknowledged by a later terminal status.
            if sent_cancel:
                time.sleep(interval)
            else:
                cancelled.wait(interval)
    except (CancelledError, RemoteFailure, DriverUnavailable):
        raise
    except Exception as error:
        raise DriverUnavailable('Remote job outcome is unavailable (' + str(identifier) + '): ' + str(error)) from error


class RemoteFailure(RuntimeError):
    pass
