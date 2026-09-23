# Приклади 10: Backend для телеметрії

У `examples/` — API, воркер і compose з postgres/rabbitmq/redis. Еталон:
`solution/main.py`.

Приклад спрощений (без `/metrics`), але запускний. Залежності з кореня
репозиторію:

```bash
pip install -r requirements.txt
```

Інфраструктура:

```bash
docker compose -f 10-backend/examples/docker-compose.yml up -d
```

API і воркер (кожен у своєму терміналі):

```bash
cd 10-backend/examples
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ uvicorn telemetry_pipeline:app --reload
DATABASE_URL=postgresql://drone:secret@localhost:5432/drone \
RABBITMQ_URL=amqp://guest:guest@localhost:5672/ \
python telemetry_worker.py
```

Перевірка наскрізного шляху:

```bash
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" \
  -d '{"drone_id":"001","alt":100,"battery":87}'
docker compose -f 10-backend/examples/docker-compose.yml \
  exec postgres psql -U drone -d drone -tAc "SELECT count(*) FROM telemetry;"
```

Очікувано: `{"status":"queued"}` і `1`.
