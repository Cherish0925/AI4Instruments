#!/usr/bin/env python3
"""Call the laboratory's advertised MCP tools from a shell-only research host."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import threading

sys.dont_write_bytecode = True


def exchange(bridge, name=None, arguments=None, timeout=90):
    """One stdio session. Never retry a tool call or cancel the underlying experiment."""
    process = subprocess.Popen(
        [sys.executable, "-B", str(bridge)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        text=True,
    )

    def send(value):
        process.stdin.write(json.dumps(dict(jsonrpc="2.0", **value), ensure_ascii=True) + "\n")
        process.stdin.flush()

    counter = 0

    def request(method, params):
        nonlocal counter
        counter += 1
        send({"id": counter, "method": method, "params": params})
        for line in process.stdout:
            response = json.loads(line)
            if response.get("id") == counter and "method" not in response:
                if "error" in response:
                    raise ValueError(str(response["error"].get("message", response["error"])))
                return response["result"]
            if "method" in response and "id" in response:
                if response["method"] == "ping":
                    send({"id": response["id"], "result": {}})
                else:
                    send(
                        {
                            "id": response["id"],
                            "error": {"code": -32601, "message": "Unsupported request"},
                        }
                    )
        raise RuntimeError("The MCP connection closed before replying; inspect the original request ID.")

    timer = threading.Timer(timeout, process.kill)
    timer.daemon = True
    timer.start()
    try:
        hello = request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "iop-lab-shell", "version": "1.0.0"},
            },
        )
        if hello.get("protocolVersion") not in ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"):
            raise ValueError("Unsupported MCP version: " + str(hello.get("protocolVersion")))
        send({"method": "notifications/initialized"})
        if name is None:
            tools, page = [], {}
            while True:
                result = request("tools/list", page)
                tools.extend(result["tools"])
                if not result.get("nextCursor"):
                    return {"tools": tools}
                page = {"cursor": result["nextCursor"]}
        result = request("tools/call", {"name": name, "arguments": arguments or {}})
        if result.get("isError"):
            raise ValueError(
                "; ".join(c["text"] for c in result.get("content", []) if c.get("type") == "text")
                or "The laboratory rejected this operation."
            )
        if result.get("structuredContent") is not None:
            return result["structuredContent"]
        content = result.get("content", [])
        if len(content) == 1 and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except ValueError:
                pass
        return content
    finally:
        try:
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        process.stdout.close()
        timer.cancel()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cmds = cli.add_subparsers(dest="action", required=True)
    cmds.add_parser("tools", help="List current tool names and input schemas")
    call = cmds.add_parser("call")
    call.add_argument("name")
    call.add_argument(
        "arguments", nargs="?", default="{}", help="JSON object, or - to read standard input"
    )
    args = cli.parse_args()
    arguments = None
    if args.action == "call":
        arguments = json.load(sys.stdin) if args.arguments == "-" else json.loads(args.arguments)
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")
    result = exchange(
        Path(__file__).resolve().parents[1] / "bridge.py", getattr(args, "name", None), arguments
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError) as exc:
        sys.exit(str(exc))
