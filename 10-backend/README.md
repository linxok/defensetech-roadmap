# 10. Backend для телеметрії

> Статус: outline

Побудувати надійний pipeline HTTP → черга → БД: без блокування event loop, з ідемпотентністю і спостережуваністю.

## Що потрібно зрозуміти

- Розділення шляхів: приймання (швидке, 202 Accepted) і обробка (воркер) — основа стійкості під навантаженням.
- RabbitMQ: durable-черги, `delivery_mode=2`, `basic_qos(prefetch_count)` і `basic_ack` лише після успішного запису.
- Ідемпотентність: `INSERT ... ON CONFLICT` за `(drone_id, ts)` — повторна доставка не створює дублів.
- PostgreSQL для телеметрії: індекси за `(drone_id, ts DESC)`, партиціювання/retention для обсягів; TimescaleDB як варіант.
- psycopg2 — синхронний: у FastAPI виконувати через `asyncio.to_thread` або пул з’єднань.
- Міграції DDL обов’язкові з першого дня: схема в коді (`CREATE TABLE` у воркері або `migrations/`), а не «руками в psql». Alembic — наступний крок.
- Спостережуваність: `/health`, `/metrics` (Prometheus-лічильники прийнятих кадрів і помилок публікації), структурні логи з `drone_id` і `trace_id`; без цього інциденти не розслідуються.

## Контрольні питання

1. Чому API має відповідати 202 до запису в БД?
2. Як зробити обробку повідомлень ідемпотентною?
3. Що станеться з чергою, якщо БД недоступна 10 хвилин?
4. Які індекси потрібні для запиту «останні 100 точок дрона»?
5. Як перевірити, що воркер не втрачає повідомлення при рестарті?

## Очікуваний результат

Pipeline з lifespan, ін’єкцією publisher-а і тестами (`solution/main.py`) + воркер із ретраями.

## Зв'язок з capstone

Розділи «Архітектура» і «Швидкий старт (режим sim)»: capstone використовує саме цей стек — сервіси `backend`, `worker`, `postgres`, `rabbitmq`.

## Типові помилки

- Створювати з’єднання при імпорті — сервіс не стартує без брокера.
- `basic_ack` до запису: втрата даних при падінні між ack і INSERT.
- Одна таблиця без індексів і retention — диск закінчується за місяці.
- Синхронний `requests.post` усередині async-коду блокує loop.

## Первинні джерела

- [RabbitMQ: AMQP 0-9-1](https://www.rabbitmq.com/tutorials/amqp-concepts) — черги, ack, prefetch, durable
- [PostgreSQL docs](https://www.postgresql.org/docs/) — індекси, ON CONFLICT, партиції
- [FastAPI: lifespan](https://fastapi.tiangolo.com/advanced/events/) — керування з’єднаннями
- [Redis docs](https://redis.io/docs/latest/) — кеш останнього стану
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) — міграції схеми

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
