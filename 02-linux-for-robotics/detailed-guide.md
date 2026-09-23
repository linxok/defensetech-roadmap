# Розширений гайд 02: Linux для робототехніки

Цикл навчання — у `docs/learning-workflow.md`. Нижче — маршрут модуля.

## Порядок проходження

1. Напишіть `read_serial.sh` і перевірте його вручну на `/dev/ttyUSB0`.
2. Оформіть unit-файл з `Restart=on-failure` і `User=dronesvc`.
3. Додайте udev-правило `SYMLINK+="ttyFC"` і перевірте `udevadm test`.
4. Запустіть сервіс і перегляньте `journalctl -u drone-telemetry -f`.
5. Змоделюйте збій (витягніть USB) і переконайтеся, що сервіс перезапустився.

## Орієнтовний час

1 тиждень (6–8 годин)

## Артефакти модуля

- `systemd-drone.service`
- `99-drone-serial.rules`
- `read_serial.sh`
- journalctl-лог перезапуску

## Пастки цього модуля

- Немає прав: додайте користувача в `dialout` і перелогіньтесь
- udev не бачить правило без `udevadm control --reload-rules`
- Без `set -euo pipefail` скрипт «проходить» з помилками
