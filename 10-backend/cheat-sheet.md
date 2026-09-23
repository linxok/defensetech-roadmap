# Cheat Sheet 10: Backend для телеметрії

- `docker compose up -d postgres rabbitmq redis`
- `channel.basic_qos(prefetch_count=10)`
- `channel.basic_ack(delivery_tag=method.delivery_tag)`
- `INSERT ... ON CONFLICT (drone_id, ts) DO NOTHING`
- `await asyncio.to_thread(blocking_call)`
- `psql "$DATABASE_URL" -c "\d+ telemetry"`
