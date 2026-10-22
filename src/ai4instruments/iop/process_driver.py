"""Native supervision for drivers supplied as independent executables."""
from __future__ import annotations
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import uuid
from concurrent.futures import CancelledError
from pathlib import Path
from .drivers import Driver


class DriverUnavailable(RuntimeError):
    """The driver stopped without confirming the physical operation's outcome."""


def executable():
    suffix = '.exe' if sys.platform == 'win32' else ''
    bundled = Path(__file__).with_name('bin') / ('iop-execd' + suffix)
    value = os.environ.get('IOP_EXECD') or (str(bundled) if bundled.is_file() else shutil.which('iop-execd'))
    if not value:
        raise ValueError('Install an IOP package containing iop-execd, or set IOP_EXECD to its executable')
    return value


class Worker:
    def __init__(self, config):
        self.lock = threading.Lock()
        self.messages = queue.Queue()
        self.failed = False
        command = config.get('command', ['{python}', '-m', 'ai4instruments.iop.worker'])
        if not isinstance(command, list) or not command or any(not isinstance(x,str) for x in command):
            raise ValueError('Worker command must be an executable and argument list')
        command = [sys.executable if x == '{python}' else x for x in command]
        self.process = subprocess.Popen([executable(), '--timeout', str(config.get('timeout',300)), '--', *command],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, text=True, encoding='utf-8', bufsize=1)
        def read():
            try:
                for line in self.process.stdout:
                    self.messages.put(json.loads(line))
            except (ValueError, OSError):
                pass
            finally:
                self.messages.put(None)
        self.reader = threading.Thread(target=read, daemon=True); self.reader.start()
        try:
            self.call('configure', config.get('configuration', {}))
        except BaseException:
            self.close()
            raise

    def send(self, message):
        try:
            self.process.stdin.write(json.dumps(message, allow_nan=False) + '\n')
            self.process.stdin.flush()
        except (BrokenPipeError, OSError):
            self.failed = True
            raise DriverUnavailable('Driver process is unavailable') from None

    def call(self, method, params, cancelled=None):
        with self.lock:
            if self.failed:
                raise DriverUnavailable('Driver requires reconnection after its last interruption')
            request_id = str(uuid.uuid4())
            self.send({'id': request_id, 'method': method, 'params': params})
            cancel_sent = False
            while True:
                if cancelled is not None and cancelled.is_set() and not cancel_sent:
                    self.send({'method':'cancel','params':{'id':request_id}})
                    cancel_sent = True
                try:
                    response = self.messages.get(timeout=0.05)
                except queue.Empty:
                    if self.process.poll() is not None:
                        self.failed = True
                        raise DriverUnavailable('Driver supervisor exited without a result')
                    continue
                if response is None or response.get('id') != request_id or response.get('outcome_unknown'):
                    self.failed = True
                    raise DriverUnavailable((response or {}).get('error','Driver exited without a result'))
                if response.get('cancelled'):
                    raise CancelledError()
                if 'error' in response:
                    raise RuntimeError(response['error'])
                return response.get('result')

    def close(self):
        if self.process.poll() is None:
            try: self.process.stdin.close()
            except OSError: pass
            try: self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait()
        self.reader.join(timeout=1)
        self.process.stdout.close()
        if not self.process.stdin.closed: self.process.stdin.close()


class ProcessDriver(Driver):
    def __init__(self, device_id, config, registry):
        super().__init__(device_id, config, registry)
        self.worker_id = config.get('worker', device_id)
        self.worker = None
        for driver in list(registry.values()):
            if isinstance(driver, ProcessDriver) and driver.worker_id == self.worker_id:
                if driver.config != config:
                    raise ValueError('Devices sharing a worker must use the same worker configuration')
                self.worker = driver.worker
                break
        created = self.worker is None
        if created:
            self.worker = Worker(config)
        try: self.description = self.worker.call('describe', {'device':device_id})
        except BaseException:
            if created: self.worker.close()
            raise
        self.description.setdefault('resources', []).append('worker:' + self.worker_id)

    def describe(self):
        return self.description

    def invoke(self, operation, arguments, cancelled):
        return self.worker.call('invoke', {'device':self.id,'operation':operation,'arguments':arguments}, cancelled)

    def close(self):
        self.worker.close()
