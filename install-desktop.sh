#!/bin/sh
set -eu
IOP_INSTALL_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export IOP_DESKTOP=1
sh "$IOP_INSTALL_ROOT/install.sh"
