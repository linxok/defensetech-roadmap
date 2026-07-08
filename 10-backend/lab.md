# Лабораторна робота 10: Telemetry Pipeline

## Мета

Побудувати end-to-end pipeline: UDP → FastAPI → RabbitMQ → Worker → PostgreSQL → API.

## Передумови

- Docker і Docker Compose.
- PostgreSQL, RabbitMQ, Redis локально або в контейнерах.

## Кроки

### 1. Docker Compose стек

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
  rabbitmq:
    image: rabbitmq:3-management
  redis:
    image: redis:7
```

### 2. FastAPI gateway

```python
from fastapi import FastAPI
import pika

app = FastAPI()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='telemetry')

@app.post("/telemetry")
def receive_telemetry(data: dict):
    channel.basic_publish(exchange='', routing_key='telemetry', body=str(data))
    return {"status": "queued"}
```

### 3. Worker

```python
import pika
import psycopg2

conn = psycopg2.connect("dbname=drone user=postgres password=secret host=localhost")
channel = pika.connection...

def callback(ch, method, properties, body):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO telemetry (drone_id, alt) VALUES (%s, %s)", (...))
    conn.commit()
```

### 4. Тестування

```bash
curl -X POST http://localhost:8000/telemetry -H "Content-Type: application/json" -d '{"drone_id":"001","alt":100}'
```

## Очікуваний результат

- Працюючий pipeline.
- Дані в PostgreSQL.
- README і docker-compose.yml.
