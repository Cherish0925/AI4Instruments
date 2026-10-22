"""Client for native process execution; program output is written directly to files."""
import json
import subprocess
import threading
import uuid
from .process_driver import executable


class NativeJob:
    def __init__(self, command, cwd, env, stdout, stderr, stdin=None, timeout=0, notify=None):
        self.id = uuid.uuid4().hex
        self.returncode = None
        self.error = None
        self.cancelled = False
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.process = subprocess.Popen([executable(), '--job'], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=None, text=True, encoding='utf-8', bufsize=1)
        self._send({'id': self.id, 'method': 'execute', 'params': {
            'command': command, 'cwd': str(cwd), 'env': env, 'stdout': str(stdout),
            'stderr': str(stderr), 'stdin': str(stdin) if stdin else None, 'timeout': timeout}})

        def read():
            try:
                for line in self.process.stdout:
                    message = json.loads(line)
                    if message.get('id') != self.id:
                        raise RuntimeError('Native executor returned an unexpected job ID')
                    if 'event' in message:
                        continue
                    self.error = message.get('error')
                    self.cancelled = message.get('cancelled', False)
                    self.returncode = message.get('result', {}).get('exit_code', -1)
                    break
            except (ValueError, OSError, RuntimeError) as error:
                self.error = str(error)
            finally:
                if self.returncode is None:
                    self.returncode = -1
                    self.error = self.error or 'Native executor exited without returning a result'
                self.done.set()
                if notify:
                    notify()
        self.reader = threading.Thread(target=read, name='iop-job', daemon=True)
        self.reader.start()

    def _send(self, message):
        with self.lock:
            self.process.stdin.write(json.dumps(message, allow_nan=False) + '\n')
            self.process.stdin.flush()

    def poll(self):
        return self.returncode if self.done.is_set() else None

    def terminate(self):
        if not self.done.is_set():
            try:
                self._send({'method': 'cancel', 'params': {'id': self.id}})
            except (BrokenPipeError, OSError, ValueError):
                pass

    def close(self):
        with self.lock:
            if not self.process.stdin.closed:
                self.process.stdin.close()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill(); self.process.wait()
        self.reader.join(timeout=1)
        self.process.stdout.close()
