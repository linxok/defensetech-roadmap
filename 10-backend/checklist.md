# Чекліст 10: Backend для телеметрії

Кожен пункт — команда або артефакт з об'єктивним результатом.
Самозвіт «зрозумів» не зараховується.

- [ ] `python checks/check_lab.py --target solution` проходить
- [ ] Імпорт `main.py` не відкриває зʼєднань (зʼєднання — у lifespan)
- [ ] Повідомлення в БД після curl
- [ ] Тест на fake-publisher зелений
- [ ] `curl localhost:8000/metrics` повертає Prometheus-текст із лічильниками

Повний прогін: `python scripts/run_lab_checks.py --module 10-backend`.
