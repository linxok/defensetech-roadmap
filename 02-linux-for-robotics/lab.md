# Лабораторна робота 02: systemd + serial daemon

## Мета

Створити systemd-сервіс `drone-telemetry`, який читає дані з USB-to-serial адаптера, записує їх у журнал journald і перезапускається при збої.

## Передумови

- Linux (Ubuntu 22.04 або WSL2).
- systemd, bash і утиліта `stty`.
- USB-to-serial адаптер (FTDI або CH340) або SITL loopback.
- Права sudo.

## Файли лабораторної

Створіть у теці здачі (`solution/`) рівно три файли — `checks/check_lab.py` шукає їх за розширеннями:

- `solution/drone-telemetry.service` — unit-файл systemd; встановлюється як `/etc/systemd/system/drone-telemetry.service`, тому в усіх командах сервіс зветься `drone-telemetry`;
- `solution/read_serial.sh` — скрипт читання serial-порту (обовʼязково з правом на виконання);
- `solution/99-drone-serial.rules` — udev-правило зі стабільним symlink.

## Кроки

### 1. Скрипт для читання serial

Скрипт приймає порт і швидкість аргументами, налаштовує tty через `stty` і виводить рядки в stdout. systemd перехоплює stdout/stderr і збирає їх у journald, тому окремий лог-файл не потрібен: сервіс працює від непривілейованого користувача і не мав би доступу до `/var/log`.

```bash
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
```

Дайте скрипту право на виконання — без цього перевірка не пройде:

```bash
chmod +x read_serial.sh
```

### 2. systemd unit

Створіть `drone-telemetry.service`. Перевірка вимагає наявності `[Unit]`, `[Service]`, `[Install]`, `ExecStart=`, `Restart=on-failure`, `After=network-online.target` і `WantedBy=multi-user.target`. Сервіс не має працювати від `root`: використовуйте `User=dronesvc` і `Group=dialout`.

```ini
[Unit]
Description=MAVLink serial telemetry daemon
Documentation=https://ardupilot.org/dev/docs/mavlink-basics.html
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=dronesvc
Group=dialout
WorkingDirectory=/opt/drone-telemetry
ExecStart=/opt/drone-telemetry/read_serial.sh /dev/ttyUSB0 57600
Restart=on-failure
RestartSec=3
StandardOutput=journal
StandardError=journal
# Обмеження: serial-порт доступний лише через DeviceAllow
DeviceAllow=/dev/ttyUSB0 rw

[Install]
WantedBy=multi-user.target
```

`Restart=always` не використовуйте: він перезапускає сервіс і після коректного завершення процесу.

### 3. udev rule

Правило створює стабільний symlink `/dev/ttyFC` і дає доступ групі `dialout`. Не використовуйте `MODE="0666"` — це відкриває пристрій усім користувачам системи; достатньо `MODE="0660"` разом із `GROUP="dialout"`.

```bash
# /etc/udev/rules.d/99-drone-serial.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0660", GROUP="dialout", SYMLINK+="ttyFC"
```

### 4. Встановлення і запуск

```bash
sudo cp drone-telemetry.service /etc/systemd/system/
sudo cp 99-drone-serial.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
sudo systemctl daemon-reload
sudo systemctl enable --now drone-telemetry
sudo journalctl -u drone-telemetry -f
```

## Перевірка

Автоматична перевірка контракту (unit, serial-скрипт, udev-правило):

```bash
python checks/check_lab.py --target solution
```

Стан сервісу і журнал старту:

```bash
systemctl status drone-telemetry
journalctl -u drone-telemetry --since "5 min ago"
```

Потім витягніть USB: сервіс має перезапуститися, а в журналі — бути причина.

## Розбір збоїв

- `Unit file ... not found` — неправильний шлях у `ExecStart`.
- Сервіс стартує до появи пристрою — додайте `After=dev-ttyFC.device`.
- `Permission denied` на порт — користувач не в групі `dialout`.
- Сервіс не перезапускається — перевірте `Restart=on-failure`, а не `Restart=always`.

## Очікуваний результат

- Сервіс `drone-telemetry` запущено, і він записує журнал у journald.
- Стабільне імʼя пристрою через udev (`/dev/ttyFC`).
- README з інструкцією.
