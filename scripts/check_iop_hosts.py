"""Exercise installed Research OS and Qiushi packages on a temporary simulated lab.

Set PYTHONPATH to the Research OS extensions directory and Qiushi product checkout.
The host packages are optional; the normal IOP installation does not import them.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from unittest.mock import patch

from ai4instruments.iop import connector
from ai4instruments.iop.config import initialize
from ai4instruments.iop.engine import Engine
from ai4instruments.iop.server import Server


async def call_installed(manifest, package, method, arguments, token):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    spec = manifest["mcpServers"]["lab"]
    assert spec["command"] == "${RESEARCH_PYTHON}" and spec["transport"] == "stdio"
    settings = StdioServerParameters(
        command=sys.executable,
        args=[s.replace("${PACKAGE_ROOT}", str(package)) for s in spec["args"]],
        env={"LAB_IOP_TEST": token},
    )
    async with stdio_client(settings) as streams, ClientSession(*streams) as session:
        await session.initialize()
        reply = await session.call_tool(method, arguments)
        assert not reply.is_error, reply
        return reply.structured_content or json.loads(reply.content[0].text)


def main():
    from aros_extensions import ExtensionStore
    from ai_scientist.extension_packages import install_extension_package

    p = argparse.ArgumentParser()
    connector.options(p)
    with tempfile.TemporaryDirectory(prefix="IOP host integration ") as temporary:
        root = Path(temporary)
        home = root / "lab"
        state = initialize(home, True, 0)
        state["discovery_interval"] = 0
        engine = Engine(home, state)
        server = Server(("127.0.0.1", 0), engine)
        engine.start()
        web = threading.Thread(target=server.serve_forever, daemon=True)
        web.start()
        workspace = root / "research"
        store = ExtensionStore(workspace / "System/state/extensions", working_root=workspace)
        try:
            args = p.parse_args(
                [
                    "--name",
                    "bench",
                    "--output",
                    str(root / "connections"),
                    "--remote",
                    engine.endpoint,
                    "--token-env",
                    "LAB_IOP_TEST",
                ]
            )
            original = connector.install(args)
            first = store.install(
                Path(original["research_os"]), kind="plugin", name="bench", operation_id="install-bench"
            )
            qtarget = root / "qiushi user" / "MCP" / "bench"
            install_extension_package(Path(original["qiushi"]), qtarget, "mcp", expected_name="bench")
            env = dict(os.environ, LAB_IOP_TEST=state["token"])

            def qiushi(method, data):
                return json.loads(
                    subprocess.check_output(
                        [str(qtarget / "bin/bench"), "call", method, "-"],
                        env=env,
                        input=json.dumps(data),
                        text=True,
                        timeout=30,
                    )
                )

            assert qiushi("lab_context", {})["status"]["devices"] == 3
            spec = {
                "steps": [{"id": "position", "device": "stage", "operation": "position"}],
                "request_id": "host-round-trip",
            }
            run = qiushi("submit_experiment", spec)
            with patch.object(connector, "VERSION", "1.0.1"):
                updated = connector.install(
                    p.parse_args(["--name", "bench", "--output", str(root / "connections")])
                )
            next_ = store.install(
                Path(updated["research_os"]),
                kind="plugin",
                name="bench",
                operation_id="update-bench",
                expected_revision=first["revision"],
            )
            install_extension_package(Path(updated["qiushi"]), qtarget, "mcp", expected_name="bench")
            archive = store.root / next_["version_path"]
            manifest = json.loads((archive / "plugin.json").read_text())
            result = asyncio.run(
                call_installed(
                    manifest,
                    archive,
                    "experiment",
                    {"run_id": run["id"], "include_result": True},
                    state["token"],
                )
            )
            assert result["run"]["state"] == "completed" and "position" in result["result"]
            assert qiushi("submit_experiment", spec)["id"] == run["id"]
            print(
                json.dumps(
                    {
                        "installed": ["research-os", "qiushi"],
                        "run_id": run["id"],
                        "state": result["run"]["state"],
                        "result": result["result"],
                        "same_id_after_update": True,
                    },
                    ensure_ascii=False,
                )
            )
        finally:
            store.close()
            server.shutdown()
            server.server_close()
            engine.close()
            web.join()


if __name__ == "__main__":
    main()
