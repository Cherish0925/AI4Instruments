"""Installed connectors share one service and keep accepted experiments across client upgrades."""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ai4instruments.iop import connector
from ai4instruments.iop.client import Client, IOPError, SameServiceRedirect
from ai4instruments.iop.config import initialize
from ai4instruments.iop.connector import bridge
from urllib.request import Request
from . import test_service as fixture


def args(root, *argv):
    parser = argparse.ArgumentParser()
    connector.options(parser)
    return parser.parse_args(["--output", str(root)] + list(argv))


class InstallCase(unittest.TestCase):
    def test_reinstall_pins_lab_and_preserves_previous_revision(self):
        with tempfile.TemporaryDirectory(prefix="IOP connector ") as d:
            root = Path(d)
            first = connector.install(args(root, "--ssh", "bench", "--remote-iop", "/opt/Lab Tools/iop"))
            self.assertEqual(connector.install(args(root)), first)
            with self.assertRaisesRegex(ValueError, "different connection"):
                connector.install(args(root, "--ssh", "another-bench"))
            major, minor, patch_version = map(int, connector.VERSION.split('.'))
            next_version = f'{major}.{minor}.{patch_version + 1}'
            with patch.object(connector, "VERSION", next_version):
                replacement = connector.install(args(root))
            self.assertNotEqual(first["revision"], replacement["revision"])
            self.assertTrue(Path(first["mcp"]).is_file())
            for manifest in [".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json"]:
                self.assertIn(
                    replacement["revision"], (Path(first["marketplace"]) / manifest).read_text()
                )
            f = Path(replacement["research_os"]) / "bridge.py"
            f.write_bytes(b"local edit")
            with (
                patch.object(connector, "VERSION", next_version),
                self.assertRaisesRegex(ValueError, "edited"),
            ):
                connector.install(args(root))
            self.assertEqual(f.read_bytes(), b"local edit")

    def test_remote_identity_and_credentials_are_not_inherited_from_a_different_lab(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {}, clear=True):
            config = initialize(root)
            self.assertEqual(Client("https://other.invalid", home=root).token, "")
            self.assertEqual(Client(home=root).token, config["token"])
            with self.assertRaises(IOPError):
                SameServiceRedirect().redirect_request(
                    Request("https://one.invalid"), None, 302, "", {}, "https://two.invalid"
                )
            profile = connector.connection(
                args(root, "--remote", "https://lab.example", "--token-env", "LAB_A")
            )
            with self.assertRaisesRegex(ValueError, "LAB_A"):
                bridge.launch(profile, {"IOP_TOKEN": "wrong"})
            cmd, env = bridge.launch(
                profile, {"LAB_A": "one", "IOP_ENDPOINT": "https://wrong", "IOP_TOKEN": "another"}
            )
            self.assertEqual(cmd[-3:], ["--endpoint", "https://lab.example", "mcp"])
            self.assertEqual(env["IOP_TOKEN"], "one")
            self.assertNotIn("IOP_ENDPOINT", env)
            with self.assertRaises(ValueError):
                connector.connection(args(root, "--remote", "https://user:password@lab.example"))

    def test_os_assigned_port_reconnects_only_to_the_saved_service(self):
        import time
        from ai4instruments.iop.config import InstanceLock

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            initialize(home, port=0)
            cli = [sys.executable, "-m", "ai4instruments.iop", "--home", tmp]
            subprocess.run([*cli, "start"], capture_output=True, check=True, timeout=20)
            try:
                saved = json.loads((home / "config.json").read_text(encoding="utf-8"))
                self.assertGreater(saved["port"], 0)
                client = Client(home=home)
                self.assertEqual(Client(client.endpoint, home=home).token, saved["token"])
                self.assertGreaterEqual(client.request("/v1/status")["devices"], 0)
                self.assertEqual(Client("http://127.0.0.1:0", home=home).token, "")
            finally:
                subprocess.run([*cli, "stop"], capture_output=True, check=True, timeout=10)
                until = time.monotonic() + 6
                while True:
                    try:
                        lock = InstanceLock(home)
                        lock.close()
                        # On Windows the child may still own its redirected output after releasing the service lock.
                        (home / "service.log").unlink(missing_ok=True)
                        break
                    except (RuntimeError, PermissionError):
                        if time.monotonic() > until:
                            raise
                        time.sleep(0.05)

    def test_headless_install_uses_explicit_paths_without_a_user_profile(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(Path, "home", side_effect=RuntimeError("no home")),
        ):
            placed = connector.install(
                args(tmp, "--local", "--lab-home", tmp, "--iop-python", sys.executable)
            )
            self.assertTrue(Path(placed["mcp"]).is_file())

    def test_ssh_is_noninteractive_and_preserves_remote_arguments(self):
        profile = connector.connection(
            args(
                ".", "--ssh", "my-lab", "--remote-iop", "/opt/Lab tools/iop", "--lab-home", "/data/Lab A"
            )
        )
        with patch("shutil.which", return_value="/bin/ssh"):
            cmd, env = bridge.launch(profile, {"IOP_TOKEN": "secret", "IOP_ENDPOINT": "wrong"})
        self.assertEqual(cmd[-2:], ["my-lab", "'/opt/Lab tools/iop' --home '/data/Lab A' mcp"])
        self.assertNotIn("IOP_TOKEN", env)
        self.assertIn("BatchMode=yes", cmd)


@unittest.skipUnless(importlib.util.find_spec("mcp"), "Install the agent extra for the MCP round trip")
class ConnectedCase(unittest.TestCase):
    setUp = fixture.ServiceCase.setUp
    tearDown = fixture.ServiceCase.tearDown

    def test_shell_and_mcp_packages_rejoin_one_run_after_update(self):
        with tempfile.TemporaryDirectory(prefix="IOP lab host ") as d:
            cfg = args(d, "--remote", self.client.endpoint, "--token-env", "LAB_TEST")
            env = dict(os.environ, LAB_TEST=self.config["token"])
            v1 = connector.install(cfg)
            shell = Path(v1["qiushi"]) / "bin/iop-lab"

            def call(path, name, data):
                return json.loads(
                    subprocess.check_output(
                        [sys.executable, str(path), "call", name, "-"],
                        input=json.dumps(data),
                        text=True,
                        env=env,
                        timeout=40,
                    )
                )

            spec = {
                "steps": [{"id": "position", "device": "stage", "operation": "position"}],
                "request_id": "connector-one",
            }
            run = call(shell, "submit_experiment", spec)
            self.client.run(run["id"]).wait(5)
            with patch.object(connector, "VERSION", "1.0.1"):
                v2 = connector.install(args(d))
            from ai4instruments.iop.connector.shell import exchange

            with patch.dict(os.environ, {"LAB_TEST": self.config["token"]}):
                result = exchange(
                    Path(v2["research_os"]) / "bridge.py",
                    "experiment",
                    {"run_id": run["id"], "include_result": True},
                )
                again = exchange(Path(v2["research_os"]) / "bridge.py", "submit_experiment", spec)
            self.assertIn("position", result["result"])
            self.assertEqual(again["id"], run["id"])
            self.assertEqual(len(self.client.request("/v1/runs")), 1)

    def test_streamable_http_requires_its_own_secret_and_supports_a_remote_host(self):
        import socket
        import threading
        import time
        import uvicorn
        from urllib.request import urlopen
        from urllib.error import HTTPError
        from ai4instruments.iop.mcp_http import application

        app = application(self.client, "gateway-test")
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        url = "http://127.0.0.1:" + str(sock.getsockname()[1]) + "/mcp"
        server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
        thread = threading.Thread(target=server.run, kwargs={"sockets": [sock]}, daemon=True)
        thread.start()

        def post(method, params, token):
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }
            if token:
                headers["Authorization"] = "Bearer " + token
            payload = json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
            ).encode()
            with urlopen(Request(url, data=payload, headers=headers), timeout=5) as r:
                return json.load(r)["result"]

        try:
            deadline = time.monotonic() + 8
            while not server.started and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(server.started)
            for wrong in (None, self.config["token"]):
                with self.assertRaises(HTTPError) as resp:
                    post("tools/list", {}, wrong)
                self.assertEqual(resp.exception.code, 401)
            hello = post(
                "initialize",
                {
                    "protocolVersion": "2025-11-25",
                    "clientInfo": {"name": "http-host", "version": "1"},
                    "capabilities": {},
                },
                "gateway-test",
            )
            self.assertEqual(hello["serverInfo"]["name"], "IOP Runtime")
            tools = {t["name"] for t in post("tools/list", {}, "gateway-test")["tools"]}
            self.assertIn("submit_experiment", tools)
            self.assertFalse(tools.intersection({"download_file", "submit_program"}))
            result = post("tools/call", {"name": "lab_context", "arguments": {}}, "gateway-test")
            self.assertFalse(result.get("isError"))
        finally:
            server.should_exit = True
            thread.join(8)
            sock.close()
