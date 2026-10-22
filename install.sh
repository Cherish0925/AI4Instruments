#!/bin/sh
set -eu
IOP_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
IOP_PREFIX=${IOP_INSTALL_DIR:-"$HOME/.local/share/ai4instruments"}
IOP_PYTHON=${IOP_PYTHON:-python3}
"$IOP_PYTHON" -c 'import sys; assert sys.version_info >= (3,10), "Python 3.10 or later is required"'
"$IOP_PYTHON" -m venv "$IOP_PREFIX/venv"
"$IOP_PREFIX/venv/bin/python" -m pip install --upgrade pip
IOP_SOURCE="$IOP_ROOT"
for IOP_WHEEL in "$IOP_ROOT"/dist/*.whl; do
    if [ -f "$IOP_WHEEL" ]; then IOP_SOURCE="$IOP_WHEEL"; break; fi
done
"$IOP_PREFIX/venv/bin/python" -m pip install "$IOP_SOURCE[devices]"
"$IOP_PREFIX/venv/bin/iop" init
printf '\nInstalled. Start with:\n  "%s/venv/bin/iop" start\nOpen the platform with:\n  "%s/venv/bin/iop" open\n' "$IOP_PREFIX" "$IOP_PREFIX"
