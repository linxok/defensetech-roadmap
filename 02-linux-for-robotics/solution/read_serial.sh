#!/usr/bin/env bash
# Читає MAVLink-потік із serial-порту і пише в journald.
set -euo pipefail

PORT="${1:-/dev/ttyUSB0}"
BAUD="${2:-57600}"

if [ ! -c "${PORT}" ]; then
    echo "serial device ${PORT} not found" >&2
    exit 1
fi

stty -F "${PORT}" "${BAUD}" cs8 -cstopb -parenb raw -echo
echo "reading MAVLink from ${PORT} @ ${BAUD}"

while read -r -t 5 line; do
    echo "${line}"
done < "${PORT}"
