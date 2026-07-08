# Лабораторна робота 02: systemd + serial daemon

## Мета

Створити системний сервіс, який читає дані з USB-to-serial адаптера і пише їх у лог.

## Передумови

- Linux (Ubuntu 22.04 або WSL2).
- Python 3, pyserial.
- USB-to-serial адаптер або SITL loopback.

## Кроки

### 1. Скрипт для читання serial

```python
import serial
import logging
import time

logging.basicConfig(filename='/var/log/drone_serial.log', level=logging.INFO)

with serial.Serial('/dev/ttyUSB0', 57600, timeout=1) as ser:
    while True:
        line = ser.readline()
        if line:
            logging.info(line.decode('utf-8', errors='ignore').strip())
        time.sleep(0.1)
```

### 2. systemd unit

```ini
[Unit]
Description=Drone Serial Logger
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/drone_serial/logger.py
Restart=always
User=drone

[Install]
WantedBy=multi-user.target
```

### 3. udev rule

```bash
# /etc/udev/rules.d/99-serial.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="drone_serial", MODE="0666"
```

### 4. Запуск

```bash
sudo cp drone-serial.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable drone-serial
sudo systemctl start drone-serial
sudo journalctl -u drone-serial -f
```

## Очікуваний результат

- Сервіс запущено і пише логи.
- Stable device name через udev.
- README з інструкцією.
