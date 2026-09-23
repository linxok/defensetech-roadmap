# Чекліст 02: Linux для робототехніки

Кожен пункт — команда або артефакт з об'єктивним результатом.
Самозвіт «зрозумів» не зараховується.

- [ ] `python checks/check_lab.py --target solution` проходить
- [ ] `systemd-analyze verify` не має помилок
- [ ] udev-правило створює стабільний symlink (перевірено після reconnect)
- [ ] `journalctl -u drone-telemetry` містить лог старту і перезапуску
- [ ] Сервіс не працює від root

Повний прогін: `python scripts/run_lab_checks.py --module 02-linux-for-robotics`.
