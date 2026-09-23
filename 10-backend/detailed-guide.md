# Розширений гайд 10: Backend для телеметрії

Цикл навчання — у `docs/learning-workflow.md`. Нижче — маршрут модуля.

## Порядок проходження

1. Підніміть compose з postgres/rabbitmq/redis.
2. Реалізуйте API з lifespan і fake-publisher у тестах.
3. Напишіть воркер із ack після запису і ретраями.
4. Додайте міграцію таблиці telemetry з індексами.
5. Запустіть `checks/check_lab.py` — контракт без брокера.

## Орієнтовний час

2 тижні (12–16 годин)

## Артефакти модуля

- `main.py`
- `worker.py`
- `docker-compose.yml`
- SQL-схема

## Пастки цього модуля

- healthcheck без `pg_isready` — гонка при старті
- Немає `prefetch_count` — один воркер захоплює все
