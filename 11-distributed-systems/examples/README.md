# Приклади 11: Розподілені системи

У `examples/` — клієнт і compose для Kafka. Еталон контракту: `solution/telemetry.proto`.

Запуск: `pip install -r requirements.txt` (venv репозиторію; для gRPC-клієнта потрібні `grpcio` і `grpcio-tools`, див. `lab.md`).

## Kafka: single-node кластер

```bash
docker compose -f examples/docker-compose-kafka.yml up -d
docker compose -f examples/docker-compose-kafka.yml exec kafka \
    kafka-topics --bootstrap-server localhost:9092 \
    --create --topic telemetry --partitions 3 --replication-factor 1
```

Контейнери всередині compose підключаються до брокера за `kafka:29092`, а клієнти з хоста — за `localhost:9092`. Саме тому в `KAFKA_ADVERTISED_LISTENERS` два listener-и: `localhost` не працює з інших контейнерів, а `kafka:29092` — з хоста.
