#!/usr/bin/env bash
# Демо: читає MAVLink-потік зі стабільного symlink /dev/ttyFC.
set -euo pipefail

PORT="${1:-/dev/ttyFC}"
BAUD="${2:-57600}"

stty -F "${PORT}" "${BAUD}" cs8 -cstopb -parenb raw -echo
cat "${PORT}"
