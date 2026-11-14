#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python3 -c 'import sys; sys.exit("Python 3.10 or newer is required" if sys.version_info < (3,10) else 0)'
if [ "$#" -eq 0 ]; then set -- --help; fi
exec python3 "$SCRIPT_DIR/tools/build_translation.py" "$@"
