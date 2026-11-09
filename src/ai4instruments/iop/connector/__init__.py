"""Build a host package bound to one laboratory. No connection is opened during installation."""

from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib
import io
import zipfile
import ipaddress
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlsplit

VERSION = "1.0.1"
HERE = Path(__file__).parent


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def options(parser):
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--local",
        action="store_true",
        help="Use the laboratory on this computer (default on first install)",
    )
    mode.add_argument(
        "--remote", metavar="URL", help="IOP REST service; run its stdio bridge on this host"
    )
    mode.add_argument(
        "--ssh", metavar="ALIAS", help="Run the stdio bridge on a lab computer using an OpenSSH alias"
    )
    parser.add_argument("--name", default="iop-lab", help="Unique installation name for this laboratory")
    parser.add_argument(
        "--output",
        type=Path,
        help="Parent of the generated marketplace",
    )
    parser.add_argument("--lab-home", help="IOP data directory on the lab computer (local or SSH)")
    parser.add_argument(
        "--iop-python", help="Absolute installed IOP Python on this host, including its agent component"
    )
    parser.add_argument("--remote-iop", help="IOP executable in the SSH account (default: iop)")
    parser.add_argument(
        "--token-env",
        help="Host environment variable holding the remote REST token (default: IOP_TOKEN)",
    )


def connection(args):
    if (
        (args.remote_iop and not args.ssh)
        or (args.token_env and not args.remote)
        or (args.remote and args.lab_home)
        or (args.ssh and args.iop_python)
    ):
        raise ValueError(
            "Use --remote-iop with --ssh, --token-env with --remote, and --lab-home with local or SSH."
        )
    if args.ssh:
        if not re.fullmatch(r"(?:[A-Za-z0-9_][\w.-]*@)?[A-Za-z0-9_][\w.-]*", args.ssh, re.ASCII):
            raise ValueError("Use an OpenSSH host name or configuration alias.")
        return dict(
            mode="ssh", host=args.ssh, remote_iop=args.remote_iop or "iop", home=args.lab_home or ""
        )
    if args.iop_python:
        python = Path(args.iop_python).expanduser()
    elif importlib.util.find_spec("ai4instruments") is not None:
        python = Path(sys.executable)
    else:
        if prefix_env := os.environ.get("IOP_INSTALL_DIR"):
            prefix = Path(prefix_env)
        elif os.name == "nt":
            base = os.environ.get("LOCALAPPDATA")
            prefix = (Path(base) if base else Path.home()) / "AI4Instruments"
        else:
            prefix = Path.home() / ".local/share/ai4instruments"
        python = prefix / ("venv/Scripts/python.exe" if os.name == "nt" else "venv/bin/python")
    if not python.is_absolute() or not python.is_file():
        raise ValueError("Specify the absolute path to the installed IOP Python with --iop-python.")
    # Keep the virtual environment executable, including when it is a symlink to system Python.
    if args.remote:
        u = urlsplit(args.remote)
        if (
            not u.hostname
            or u.scheme not in ("https", "http")
            or u.username is not None
            or u.password is not None
            or u.query
            or u.fragment
            or u.path not in ("", "/")
        ):
            raise ValueError(
                "Use the IOP service origin, without credentials, /v1, a query or a fragment."
            )
        try:
            loopback = ipaddress.ip_address(u.hostname).is_loopback
        except ValueError:
            loopback = u.hostname.lower() == "localhost"
        if u.scheme == "http" and not loopback:
            raise ValueError("Use HTTPS for a remote service, or HTTP on a local tunnel.")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", args.token_env or "IOP_TOKEN"):
            raise ValueError("--token-env names an environment variable; do not pass a credential.")
        return dict(
            mode="remote",
            python=str(python),
            endpoint=args.remote.rstrip("/"),
            credential={"env": args.token_env or "IOP_TOKEN"},
        )
    return dict(
        mode="local",
        python=str(python),
        home=str(
            Path(args.lab_home or os.environ.get("IOP_HOME") or Path.home() / ".iop")
            .expanduser()
            .resolve()
        ),
    )


def skill():
    installed = HERE / "SKILL.md"
    if installed.is_file():
        return installed.read_bytes()
    return (HERE.parents[3] / "iop/connect/skills/iop-lab/SKILL.md").read_bytes()


def files_for(name, profile):
    desc = "Operate instruments and retrieve experiments from the " + name + " laboratory."
    native = {
        "name": name,
        "version": VERSION,
        "description": desc,
        "author": {"name": "AI4Instruments"},
    }
    bridge = (HERE / "bridge.py").read_bytes()
    saved = encoded(profile)
    guide = skill()
    provided = {
        key + "/" + path: content
        for key in ("aros/" + name, "qiushi/" + name, "stdio")
        for path, content in [("bridge.py", bridge), ("connection.json", saved)]
    }
    for host in ("native", "aros"):
        provided[f"{host}/{name}/skills/iop-lab/SKILL.md"] = guide
    references = (
        {profile["credential"]["env"]: "${" + profile["credential"]["env"] + "}"}
        if profile["mode"] == "remote"
        else {}
    )
    server = {
        "transport": "stdio",
        "command": "${RESEARCH_PYTHON}",
        "args": ["-B", "${PACKAGE_ROOT}/bridge.py"],
        "protocol_version": "2025-11-25",
    }
    if references:
        server["env"] = references
    provided["aros/" + name + "/plugin.json"] = encoded(
        dict(native, skills=["skills/iop-lab"], mcpServers={"lab": server})
    )
    provided["qiushi/" + name + "/manifest.json"] = encoded(
        dict(
            native,
            transport="runtime-guide",
            command="MCP/" + name + "/bin/" + name,
            description=desc
            + " Use "
            + name
            + " tools or "
            + name
            + " call TOOL JSON through run_shell.",
        )
    )
    provided["qiushi/" + name + "/bin/" + name] = (HERE / "shell.py").read_bytes()
    provided["qiushi/" + name + "/MCP.md"] = (
        f"---\nname: {name}\ndescription: {desc}\n---\n\n"
        f"Run `{name} tools` for names and schemas. Use `{name} call lab_context` first. "
        f"Use `{name} call TOOL -` to read a JSON object from standard input.\n\n"
    ).encode() + guide.split(b"---", 2)[-1].lstrip()
    provided["native/" + name + "/.claude-plugin/plugin.json"] = encoded(native)
    provided["native/" + name + "/.codex-plugin/plugin.json"] = encoded(
        dict(native, skills="./skills/", mcpServers="./codex.mcp.json")
    )
    return provided


def publish(path, data):
    if path.is_file() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


@contextmanager
def install_lock(root):
    with (root / ".install.lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt

            if not lock.seek(0, 2):
                lock.write(b"0")
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def install(args):
    name = args.name
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,47}", name):
        raise ValueError("Use a laboratory name of 1–48 lowercase letters, digits and hyphens.")
    output = args.output if args.output is not None else Path.home() / ".iop-connect"
    root = output.expanduser().resolve() / name
    root.mkdir(parents=True, mode=0o700, exist_ok=True)
    with install_lock(root):
        return install_locked(args, name, root)


def install_locked(args, name, root):
    marker = root / "connection.json"
    selected = any(
        (
            args.local,
            args.remote,
            args.ssh,
            args.lab_home,
            args.iop_python,
            args.remote_iop,
            args.token_env,
        )
    )
    previous = json.loads(marker.read_text(encoding="utf-8")) if marker.is_file() else None
    if previous is None and any(p.name != ".install.lock" for p in root.iterdir()):
        raise ValueError("Choose an empty directory for this laboratory connection.")
    profile = connection(args) if selected or previous is None else previous
    if previous is not None and profile != previous:
        raise ValueError("This name already identifies a different connection. Choose another --name.")
    files = files_for(name, profile)
    publish(marker, encoded(profile))
    digest = hashlib.sha256()
    # The executable and root are part of host-specific configuration.
    for part in (str(root), sys.executable, VERSION, (HERE / "__init__.py").read_text(encoding="utf-8")):
        digest.update(part.encode() + b"\x00")
    for path, data in sorted(files.items()):
        digest.update(path.encode() + b"\x00" + hashlib.sha256(data).digest())
    rev = digest.hexdigest()[:24]
    revision = root / "packages" / rev
    descriptor = {"command": sys.executable, "args": ["-B", str(revision / "stdio/bridge.py")]}
    claude = descriptor.copy()
    codex = descriptor.copy()
    if profile["mode"] == "remote":
        key = profile["credential"]["env"]
        claude["env"] = {key: "${" + key + "}"}
        codex["env_vars"] = [key]
    files["mcp.json"] = encoded({"mcpServers": {name: descriptor}})
    files["native/" + name + "/.mcp.json"] = encoded({"mcpServers": {name: claude}})
    files["native/" + name + "/codex.mcp.json"] = encoded({"mcpServers": {name: codex}})
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    toml = (
        "[mcp_servers."
        + name
        + "]\ncommand = "
        + quote(descriptor["command"])
        + "\nargs = "
        + quote(descriptor["args"])
        + "\n"
    )
    if "env_vars" in codex:
        toml += "env_vars = " + quote(codex["env_vars"]) + "\n"
    files["codex.toml"] = toml.encode()
    # Web workspaces can upload the same Qiushi package with its executable bit intact.
    packed = io.BytesIO()
    with zipfile.ZipFile(packed, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(files.items()):
            if path.startswith("qiushi/" + name + "/"):
                entry = zipfile.ZipInfo(path.removeprefix("qiushi/"), (2020, 1, 1, 0, 0, 0))
                entry.create_system = 3
                entry.external_attr = (0o100755 if "/bin/" in path else 0o100644) << 16
                archive.writestr(entry, data, compress_type=zipfile.ZIP_DEFLATED)
    files["qiushi/" + name + ".zip"] = packed.getvalue()
    revision.parent.mkdir(exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".build-", dir=revision.parent))
    try:
        for key, data in files.items():
            path = temp / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if "/bin/" in key:
                path.chmod(0o755)
        if not revision.exists():
            try:
                temp.rename(revision)
            except OSError:
                if not revision.is_dir():
                    raise
        for key, data in files.items():
            if (revision / key).read_bytes() != data:
                raise ValueError("The installed package was edited: " + str(revision / key))
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    relative = "./packages/" + rev + "/native/" + name
    market = "iop-" + name
    publish(
        root / ".claude-plugin/marketplace.json",
        encoded(
            {
                "name": market,
                "owner": {"name": "AI4Instruments"},
                "plugins": [{"name": name, "source": relative}],
            }
        ),
    )
    publish(
        root / ".agents/plugins/marketplace.json",
        encoded(
            {
                "name": market,
                "plugins": [
                    {
                        "name": name,
                        "source": {"source": "local", "path": relative},
                        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                        "category": "Productivity",
                    }
                ],
            }
        ),
    )
    return dict(
        laboratory=name,
        connector_version=VERSION,
        revision=rev,
        marketplace=str(root),
        mcp=str(revision / "mcp.json"),
        codex_toml=str(revision / "codex.toml"),
        research_os=str(revision / "aros" / name),
        qiushi=str(revision / "qiushi" / name),
        qiushi_zip=str(revision / "qiushi" / (name + ".zip")),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options(parser)
    try:
        print(json.dumps(install(parser.parse_args()), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + "\n")
