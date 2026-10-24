#!/bin/sh
set -eu
IOP_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
IOP_PREFIX=${IOP_INSTALL_DIR:-"$HOME/.local/share/ai4instruments"}
if [ -f "$IOP_ROOT/runtime/python.tar.gz" ] && [ -z "${IOP_PYTHON:-}" ]; then
    mkdir -p "$IOP_PREFIX/runtime/0.8.2"
    tar -xzf "$IOP_ROOT/runtime/python.tar.gz" -C "$IOP_PREFIX/runtime/0.8.2"
    IOP_PYTHON="$IOP_PREFIX/runtime/0.8.2/python/bin/python3"
    IOP_BUNDLED=1
else
    IOP_PYTHON=${IOP_PYTHON:-python3}
fi
"$IOP_PYTHON" -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10 or later is required"'
if [ -f "$IOP_PREFIX/venv/bin/python" ]; then
    "$IOP_PREFIX/venv/bin/python" "$IOP_ROOT/scripts/prepare_iop_upgrade.py"
    "$IOP_PYTHON" -m venv --upgrade "$IOP_PREFIX/venv"
else
    "$IOP_PYTHON" -m venv "$IOP_PREFIX/venv"
fi
if [ -d "$IOP_ROOT/runtime/wheels" ]; then
    "$IOP_PREFIX/venv/bin/python" -m pip install --no-index --find-links "$IOP_ROOT/runtime/wheels" --upgrade pip
else
    "$IOP_PREFIX/venv/bin/python" -m pip install --upgrade pip
fi
IOP_SOURCE="$IOP_ROOT"
for IOP_WHEEL in "$IOP_ROOT"/dist/*.whl; do
    if [ -f "$IOP_WHEEL" ]; then IOP_SOURCE="$IOP_WHEEL"; break; fi
done
IOP_EXTRAS=devices
if [ "${IOP_AGENT:-1}" = "1" ]; then IOP_EXTRAS="$IOP_EXTRAS,agent"; fi
if [ "${IOP_DESKTOP:-0}" = "1" ]; then IOP_EXTRAS="$IOP_EXTRAS,desktop"; fi
if [ -d "$IOP_ROOT/runtime/wheels" ] && [ "${IOP_BUNDLED:-0}" = "1" ] && [ "${IOP_DESKTOP:-0}" != "1" ]; then
    "$IOP_PREFIX/venv/bin/python" -m pip install --no-index --find-links "$IOP_ROOT/runtime/wheels" "$IOP_SOURCE[$IOP_EXTRAS]"
else
    "$IOP_PREFIX/venv/bin/python" -m pip install --prefer-binary "$IOP_SOURCE[$IOP_EXTRAS]"
fi
"$IOP_PREFIX/venv/bin/iop" init
printf '\nInstalled. Start with:\n  "%s/venv/bin/iop" start\nOpen the platform with:\n  "%s/venv/bin/iop" open\n' "$IOP_PREFIX" "$IOP_PREFIX"
printf 'Read laboratory setup:\n  "%s/venv/bin/iop" context --start\nAgent connection settings:\n  "%s/venv/bin/iop" mcp-config\n' "$IOP_PREFIX" "$IOP_PREFIX"

if [ "${IOP_DESKTOP:-0}" = "1" ]; then
    "$IOP_PREFIX/venv/bin/iop" shortcuts
    printf '\nOpen IOP Runtime from your application menu, or run:\n  "%s/venv/bin/iop" desktop\n' "$IOP_PREFIX"
fi
