# Лабораторна робота 11: gRPC Service Mesh

## Мета

Побудувати два gRPC-сервіси: telemetry-service та command-service, які спілкуються через gRPC.

## Передумови

- Python 3.11+
- `grpcio`, `grpcio-tools`

## Кроки

### 1. Визначення proto

```protobuf
syntax = "proto3";

service TelemetryService {
  rpc SendTelemetry (TelemetryFrame) returns (Ack);
}

message TelemetryFrame {
  string drone_id = 1;
  double lat = 2;
  double lon = 3;
  float alt = 4;
}

message Ack {
  bool ok = 1;
}
```

### 2. Генерація коду

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. telemetry.proto
```

### 3. Сервер

```python
from concurrent import futures
import grpc
import telemetry_pb2
import telemetry_pb2_grpc

class TelemetryServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def SendTelemetry(self, request, context):
        print(f"Received from {request.drone_id}: {request.lat}, {request.lon}")
        return telemetry_pb2.Ack(ok=True)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryServicer(), server)
server.add_insecure_port('[::]:50051')
server.start()
server.wait_for_termination()
```

### 4. Клієнт

```python
import grpc
import telemetry_pb2
import telemetry_pb2_grpc

channel = grpc.insecure_channel('localhost:50051')
stub = telemetry_pb2_grpc.TelemetryServiceStub(channel)
frame = telemetry_pb2.TelemetryFrame(drone_id='001', lat=50.45, lon=30.52, alt=100)
ack = stub.SendTelemetry(frame)
print(ack.ok)
```

### 5. Тестування

```bash
python server.py
python client.py
```

## Перевірка

Згенеруйте код із proto та проженіть контрактну перевірку:

```bash
python checks/check_lab.py --target solution
```

Для сервера/клієнта: запустіть локально й перевірте стрімінг із deadline.

## Розбір збоїв

- Версії grpcio і grpcio-tools різняться — генерація не збігається з рантаймом
- Без deadline клієнт висить при недоступному сервері
- Перевикористані номери тегів ламають сумісність

## Очікуваний результат

- gRPC сервер і клієнт.
- `.proto` файл.
- README.
