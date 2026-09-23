# Cheat Sheet 02: Linux для робототехніки

- `systemctl daemon-reload && systemctl restart drone-telemetry`
- `journalctl -u drone-telemetry -f --since "1 hour ago"`
- `udevadm control --reload-rules && udevadm trigger`
- `udevadm info --attribute-walk --name=/dev/ttyUSB0`
- `stty -F /dev/ttyUSB0 57600 cs8 -cstopb -parenb raw -echo`
- `ip link set can0 up type can bitrate 500000`
