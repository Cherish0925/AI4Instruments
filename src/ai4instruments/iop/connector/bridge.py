"""Start one MCP bridge for one saved laboratory connection. No device state lives here."""

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path


def launch(profile, environment):
    env = environment.copy()
    # An unrelated shell's settings must never change the selected instrument service.
    for key in ("IOP_ENDPOINT", "IOP_TOKEN", "IOP_HOME"):
        env.pop(key, None)
    mode = profile["mode"]
    if mode == "ssh":
        ssh = shutil.which("ssh", path=env.get("PATH"))
        if not ssh:
            raise ValueError("Install the OpenSSH client on this computer.")
        remote = [profile["remote_iop"]]
        if profile.get("home"):
            remote += ["--home", profile["home"]]
        remote.append("mcp")
        return [
            ssh,
            "-T",
            "-o",
            "BatchMode=yes",
            "-o",
            "ClearAllForwardings=yes",
            "--",
            profile["host"],
            shlex.join(remote),
        ], env
    args = [profile["python"], "-m", "ai4instruments.iop"]
    if mode == "remote":
        name = profile["credential"]["env"]
        token = environment.get(name)
        if not token:
            raise ValueError("The selected laboratory requires the host secret " + name + ".")
        env["IOP_TOKEN"] = token
        args += ["--endpoint", profile["endpoint"]]
    elif mode == "local":
        args += ["--home", profile["home"]]
    else:
        raise ValueError("Unknown laboratory connection: " + str(mode))
    return args + ["mcp"], env


def command():
    config = json.loads(Path(__file__).with_name("connection.json").read_text(encoding="utf-8"))
    return launch(config, os.environ)


def main():
    argv, env = command()
    if os.name == "nt":
        return subprocess.call(argv, env=env)
    os.execve(argv[0], argv, env)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        sys.exit(str(exc))
