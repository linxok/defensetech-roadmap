# Сертифікаційний чекліст

Об'єктивні критерії замість «прочитав модуль». Кожен пункт можна
перевірити командою або артефактом. Позначайте лише те, що
підтверджено виводом команд.

## Рівень 1: Foundation (модулі 00–03)

- [ ] `python scripts/verify_structure.py` завершується без помилок
- [ ] `python scripts/sitl_smoke.py --source udp:127.0.0.1:14550` бачить heartbeat і позицію
- [ ] `python 00-introduction/checks/check_lab.py --target 00-introduction/solution` — PASS
- [ ] `python 01-defense-fundamentals/checks/check_lab.py --target 01-defense-fundamentals/solution` — PASS
- [ ] `python 02-linux-for-robotics/checks/check_lab.py --target 02-linux-for-robotics/solution` — PASS
- [ ] `python 03-networking/checks/check_lab.py --target 03-networking/solution` — PASS
- [ ] У власному репозиторії є `plan.md` із датами та числами годин

## Рівень 2: Core code (модулі 04–05)

- [ ] `python 04-python/checks/check_lab.py --target 04-python/solution` — PASS
- [ ] `python 05-modern-cpp/checks/check_lab.py --target 05-modern-cpp/solution` — PASS
- [ ] Ваш Telemetry API повертає 422 на battery=150 (перевірено curl)
- [ ] Ваш thread pool виводить `sum_of_squares=204` без зависань

## Рівень 3: Drone middleware (модулі 06–09)

- [ ] `python 06-mavlink/checks/check_lab.py --target 06-mavlink/solution` — PASS
- [ ] `python 07-ardupilot/checks/check_lab.py --target 07-ardupilot/solution` — PASS
- [ ] `python 08-px4/checks/check_lab.py --target 08-px4/solution` — PASS
- [ ] `python 09-ros2/checks/check_lab.py --target 09-ros2/solution` — PASS
- [ ] Gateway публікує JSON у WebSocket і не має `asyncio.wait(` у коді
- [ ] ARM/takeoff/RTL у SITL підтверджені COMMAND_ACK
- [ ] Failsafe RTL відтворено і задокументовано (модулі 06–08)
- [ ] ULog-звіт містить 5+ метрик з одиницями (модуль 08)

## Рівень 4: System (модулі 10, 14–15 + capstone)

- [ ] `python 10-backend/checks/check_lab.py --target 10-backend/solution` — PASS
- [ ] `python 14-ground-control/checks/check_lab.py --target 14-ground-control/solution` — PASS
- [ ] `python 15-devops/checks/check_lab.py --target 15-devops/solution` — PASS
- [ ] `cd capstone && docker compose up --build` показує телеметрію в UI
- [ ] `docker compose -f capstone/docker-compose.yml build` завершується успішно
- [ ] `python -m pytest capstone/tests -q` — зелено
- [ ] Заміряно наскрізну затримку sim → UI і записано в README

## Рівень 5: Career (модулі 16–17)

- [ ] `python 16-projects/checks/check_lab.py --target 16-projects/solution` — PASS
- [ ] `python 17-interview/checks/check_lab.py --target 17-interview/solution` — PASS
- [ ] Два публічні репозиторії з README, тестами і зеленим CI
- [ ] Демо-відео capstone до 2 хвилин
- [ ] 10+ відповідей у `answers.md` без заглушок і з числами
- [ ] Проведено 2 мок-співбесіди з фідбеком
- [ ] ≥10 відгуків на вакансії треку

## Повний прогін (перед співбесідою)

```bash
python scripts/verify_structure.py
python scripts/check_duplicates.py
python scripts/run_lab_checks.py
python -m pytest -q
python scripts/prepare_docs.py
mkdocs build --strict -f .mkdocs-build/mkdocs.yml
```

Очікування: 18 passed у lab-check, зелений pytest, strict-збірка сайту.
Якщо щось падає — це і є наступне завдання, а не «відоме обмеження».
