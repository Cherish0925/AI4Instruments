"""Adapt command-line solvers, analysis programs and vendor executables to IOP."""
import json
import math
import os
import sys
from concurrent.futures import CancelledError
from pathlib import Path
from .drivers import Driver
from .jobs import NativeJob


class Command(Driver):
    def describe(self):
        operations = self.config.get('operations', {})
        for name, spec in operations.items():
            command = spec.get('command', self.config.get('command'))
            if not isinstance(command, list) or not command or any(not isinstance(v, str) or not v for v in command):
                raise ValueError('Command operation needs an executable and argument array: ' + name)
            timeout = spec.get('timeout', self.config.get('timeout', 0))
            if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout < 0:
                raise ValueError('Program timeout must be nonnegative; zero allows any duration')
        return {'name': self.config.get('name', self.id), 'mode': self.config.get('mode', 'software'),
                'transport': 'command', 'concurrency': self.config.get('concurrency', 1),
                'requirements': self.config.get('requirements', {}), 'operations': operations}

    def invoke(self, operation, arguments, cancelled):
        if cancelled.is_set():
            raise CancelledError()
        if not hasattr(cancelled, 'output_dir'):
            raise ValueError('Command operations need an IOP execution context')
        folder = cancelled.output_dir
        folder.mkdir(parents=True, exist_ok=True)
        spec = self.config['operations'][operation]
        request = {'operation': operation, 'arguments': arguments, 'run_id': cancelled.run_id,
                   'operation_id': cancelled.operation_id, 'output_dir': str(folder)}
        request_file = folder / 'request.json'
        request_file.write_text(json.dumps(request, allow_nan=False), encoding='utf-8')
        env = os.environ.copy()
        env.update(self.config.get('env', {}))
        env.update(IOP_ARGUMENTS_JSON=json.dumps(arguments, allow_nan=False), IOP_OPERATION=operation,
                   IOP_RUN_ID=cancelled.run_id, IOP_OPERATION_ID=cancelled.operation_id,
                   IOP_OUTPUT_DIR=str(folder), IOP_REQUEST_FILE=str(request_file),
                   IOP_RESULT_FILE=str(folder / 'result.json'), IOP_PROGRESS_FILE=str(folder / 'progress.json'))
        replacements = {'{python}': sys.executable, '{request}': str(request_file), '{output}': str(folder),
                        '{result}': str(folder / 'result.json')}
        def argument(value):
            if value in replacements:
                return replacements[value]
            if value.startswith('${') and value.endswith('}'):
                item = arguments[value[2:-1]]
                return item if isinstance(item, str) else json.dumps(item, allow_nan=False)
            return value
        command = [argument(v) for v in spec.get('command', self.config.get('command'))]
        cwd = Path(self.config.get('cwd', folder)).expanduser().resolve()
        job = NativeJob(command, cwd, env, folder / 'stdout.txt', folder / 'stderr.txt', request_file,
                        timeout=spec.get('timeout', self.config.get('timeout', 0)))
        last_progress = None
        cancel_sent = False
        try:
            while not job.done.wait(0.1):
                if cancelled.is_set() and not cancel_sent:
                    job.terminate(); cancel_sent = True
                progress_file = folder / 'progress.json'
                if progress_file.is_file():
                    try:
                        value = json.loads(progress_file.read_text(encoding='utf-8'))
                    except (ValueError, OSError):
                        continue  # the producer may still be replacing the file
                    if value != last_progress:
                        cancelled.progress(**value)
                        last_progress = value
            if job.cancelled:
                raise CancelledError()
            if job.error or job.returncode:
                raise RuntimeError(job.error or 'Program exited with code ' + str(job.returncode))
            result_file = folder / 'result.json'
            result = json.loads(result_file.read_text(encoding='utf-8')) if result_file.is_file() else {'exit_code': 0}
            cancelled.progress(1, 'Completed')
            return result
        finally:
            job.close()
