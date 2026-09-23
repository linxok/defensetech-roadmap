# Cheat Sheet 11: Розподілені системи

- `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. telemetry.proto`
- `stub.StreamTelemetry(iter(frames), timeout=5)`
- Kafka: `partitions = hash(drone_id) % N`
- `kafka-topics.sh --create --partitions 12 --replication-factor 3`
- DDS QoS: RELIABLE / BEST_EFFORT / TRANSIENT_LOCAL
