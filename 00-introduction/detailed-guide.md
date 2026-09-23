# Розширений гайд 00: Вступ

Цикл навчання — у `docs/learning-workflow.md`. Нижче — маршрут модуля.

## Порядок проходження

1. Прочитайте `README.md` курсу та `ROADMAP.md`, виберіть трек.
2. Заповніть `solution/plan-example.md` своїми даними і збережіть як `plan.md`.
3. Встановіть залежності: `pip install -r requirements.txt -r requirements-dev.txt`.
4. Запустіть `python scripts/run_lab_checks.py` — переконайтеся, що середовище живе.
5. Запустіть capstone у режимі sim і подивіться телеметрію в браузері.

## Орієнтовний час

1 тиждень (4–6 годин)

## Артефакти модуля

- `plan.md` з мілстоунами
- налаштований venv
- скріншот capstone UI

## Пастки цього модуля

- Docker без прав — перевірте `docker run hello-world`
- порт 3000 зайнятий — `ss -ltnp` покаже процес
