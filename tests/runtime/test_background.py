"""Exercise the installed command as separate client and service processes."""
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from pathlib import Path
from ai4instruments.iop import Client
from ai4instruments.iop.config import initialize, InstanceLock


class BackgroundCase(unittest.TestCase):
    def test_service_binding_does_not_require_name_resolution(self):
        from types import SimpleNamespace
        from ai4instruments.iop.server import Server
        with patch('socket.getfqdn',side_effect=AssertionError('No reverse DNS needed')):
            server=Server(('127.0.0.1',0),SimpleNamespace())
            server.server_close()

    def test_detached_service_outlives_client_and_stops(self):
        with tempfile.TemporaryDirectory() as home:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            initialize(home,True,port)
            command=[sys.executable,'-m','ai4instruments.iop','--home',home]
            client=Client(home=home,timeout=1)
            try:
                try:
                    with ThreadPoolExecutor(max_workers=3) as pool:
                        starts = list(pool.map(lambda _: subprocess.run(command+['start'],check=True,capture_output=True,text=True,timeout=20), range(3)))
                    self.assertEqual(len(starts), 3)
                except (subprocess.CalledProcessError,subprocess.TimeoutExpired) as error:
                    log=Path(home)/'service.log'
                    self.fail(str(error)+'\n'+str(error.stderr)+'\n'+(log.read_text() if log.exists() else 'No service log'))
                submit="import sys; from ai4instruments.iop import Client; print(Client(home=sys.argv[1]).submit([{'id':'wait','device':'aux','operation':'wait','arguments':{'duration':0.3}}]).id)"
                run_id=subprocess.check_output([sys.executable,'-c',submit,home],text=True,timeout=10).strip()
                self.assertEqual(client.run(run_id).wait(5)['state'],'completed')
                second=subprocess.run(command+['start'],check=True,capture_output=True,text=True,timeout=10)
                self.assertIn('already running',second.stdout)
                with patch.dict('os.environ', {'IOP_ENDPOINT':'http://127.0.0.1:1', 'IOP_TOKEN':'another-service'}):
                    local=subprocess.run(command+['start'],check=True,capture_output=True,text=True,timeout=10)
                self.assertIn('already running',local.stdout)
            finally:
                try:client.request('/v1/shutdown',{})
                except OSError:pass
                deadline=time.monotonic()+10
                while time.monotonic()<deadline:
                    try:
                        lock=InstanceLock(home);lock.close()
                        # The process closes its inherited log handle on exit.
                        log=Path(home)/'service.log'
                        log.unlink()
                        break
                    except (RuntimeError,OSError):time.sleep(0.05)
                else:self.fail('Background service did not finish')


if __name__=='__main__':unittest.main()
