# Приклади 02: Linux для робототехніки

У `examples/` — демонстраційні `read_serial.sh` і `drone-telemetry.service`. Це спрощений варіант еталона з `solution/`; для здачі лабораторної використовуйте `lab.md`.

## systemd

```bash
chmod +x read_serial.sh
sudo cp drone-telemetry.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now drone-telemetry
journalctl -u drone-telemetry -f
```

## udev

```bash
sudo cp ../solution/99-drone-serial.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
ls -l /dev/ttyFC
```

Перед запуском перевірте права на порт: `id` і `ls -l /dev/ttyUSB0`. Якщо заліза немає, змоделюйте порт через socat.
