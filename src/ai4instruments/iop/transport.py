"""Reusable HTTP connections; each in-flight request owns its connection."""
import http.client
import threading
import time
from urllib.parse import urlsplit


class Connections:
    def __init__(self, maximum_idle=8):
        self.lock = threading.Lock()
        self.idle = []
        self.maximum_idle = maximum_idle

    def request(self, url, data, headers, timeout):
        target = urlsplit(url)
        key = (target.scheme, target.hostname, target.port)
        connection = None
        with self.lock:
            while self.idle:
                saved_key, timestamp, candidate = self.idle.pop()
                if saved_key == key and time.monotonic() - timestamp < 20:
                    connection = candidate
                    break
                candidate.close()
        factory = http.client.HTTPSConnection if target.scheme == 'https' else http.client.HTTPConnection
        connection = connection or factory(target.hostname, target.port, timeout=timeout)
        connection.timeout = timeout
        if connection.sock:
            connection.sock.settimeout(timeout)
        reusable = False
        try:
            path = target.path or '/'
            if target.query:
                path += '?' + target.query
            connection.request('POST' if data is not None else 'GET', path, body=data, headers=headers)
            response = connection.getresponse()
            payload = response.read()
            reusable = not response.will_close
            return response.status, payload, response.getheader('Location')
        finally:
            with self.lock:
                if reusable and len(self.idle) < self.maximum_idle:
                    self.idle.append((key, time.monotonic(), connection))
                else:
                    connection.close()

    def close(self):
        with self.lock:
            for _, _, connection in self.idle:
                connection.close()
            self.idle.clear()

    def __del__(self):
        self.close()
