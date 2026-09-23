# Лабораторна робота 11: gRPC-стрімінг телеметрії

## Мета

Описати контракт потоку телеметрії у `telemetry.proto` (client-streaming RPC) і реалізувати сервер та клієнт на згенерованому коді.

## Передумови

- Python 3.11+.
- Пакети `grpcio` і `grpcio-tools` у окремому venv: `grpcio-tools` вимагає `protobuf>=5.26.1,<6`, а `mavsdk` із кореневого `requirements.txt` — `protobuf<=3.20.1`, тому в одному середовищі вони конфліктують.

```bash
python3 -m venv .venv-grpc
source .venv-grpc/bin/activate
pip install grpcio==1.64.1 grpcio-tools==1.64.1
```

Ті самі версії зафіксовані у `requirements-grpc.txt` у корені
репозиторію — його можна встановити замість ручного піна.

## Кроки

### 1. Робоча тека

Створіть окрему теку для лабораторної, щоб згенерований код не змішувався з матеріалами курсу:

```bash
mkdir -p ~/drone-labs/11-grpc
cd ~/drone-labs/11-grpc
```

### 2. Контракт `telemetry.proto`

Створіть файл `telemetry.proto` з таким вмістом:

```protobuf
syntax = "proto3";

package telemetry.v1;

// Кадр телеметрії від одного дрона.
message TelemetryFrame {
  string drone_id = 1;
  int64 timestamp_ms = 2;
  double lat = 3;
  double lon = 4;
  double alt = 5;
  int32 battery = 6;
}

message DroneRequest {
  string drone_id = 1;
}

message Ack {
  bool accepted = 1;
  int32 received = 2;
}

service Telemetry {
  // client-streaming: дрон шле потік кадрів, сервер відповідає один раз.
  rpc StreamTelemetry(stream TelemetryFrame) returns (Ack);
  // unary: останній відомий кадр дрона.
  rpc GetLast(DroneRequest) returns (TelemetryFrame);
}
```

Що тут важливо:

- `package telemetry.v1` фіксує версію контракту: нову несумісну схему додають як `telemetry.v2`, не змінюючи теги.
- `rpc StreamTelemetry(stream TelemetryFrame) returns (Ack)` — це **client streaming**: клієнт передає потік кадрів, сервер накопичує їх і повертає один `Ack` після завершення потоку. Для телеметрії це дешевше за кадр-на-запит: одне HTTP/2-з'єднання, батчинг і backpressure.
- `rpc GetLast(DroneRequest) returns (TelemetryFrame)` — unary-запит останнього відомого кадру, потрібен для підключення нового споживача.
- Номери тегів (`= 1`, `= 2`, ...) — частина контракту: їх не можна перевикористовувати чи змінювати.

### 3. Генерація коду

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. telemetry.proto
```

Команда створює `telemetry_pb2.py` (повідомлення) і `telemetry_pb2_grpc.py` (стаби та сервіс).

### 4. Сервер

Створіть `server.py`:

```python
"""Client-streaming сервер телеметрії."""

import threading
from concurrent import futures

import grpc
import telemetry_pb2
import telemetry_pb2_grpc


class TelemetryServicer(telemetry_pb2_grpc.TelemetryServicer):
    def __init__(self):
        self._lock = threading.Lock()
        self._last = {}

    def StreamTelemetry(self, request_iterator, context):
        received = 0
        for frame in request_iterator:
            with self._lock:
                self._last[frame.drone_id] = frame
            received += 1
        return telemetry_pb2.Ack(accepted=True, received=received)

    def GetLast(self, request, context):
        with self._lock:
            frame = self._last.get(request.drone_id)
        if frame is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f'no telemetry for {request.drone_id}')
        return frame


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_TelemetryServicer_to_server(TelemetryServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('listening on [::]:50051')
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
```

Зверніть увагу: метод `StreamTelemetry` приймає `request_iterator` (потік), а не один `request`, і повертає `Ack(accepted=True, received=received)` після завершення потоку. `GetLast` — звичайний unary-метод із одним `request`.

### 5. Клієнт

Створіть `client.py`:

```python
"""Клієнт: шле потік кадрів, потім запитує останній."""

import sys

import grpc
import telemetry_pb2
import telemetry_pb2_grpc

TIMEOUT = 5.0


def frames(count=5):
    for seq in range(count):
        yield telemetry_pb2.TelemetryFrame(
            drone_id='001',
            timestamp_ms=1_700_000_000_000 + seq,
            lat=50.4501,
            lon=30.5234,
            alt=100.0 + seq,
            battery=95 - seq,
        )


def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = telemetry_pb2_grpc.TelemetryStub(channel)
        try:
            ack = stub.StreamTelemetry(frames(), timeout=TIMEOUT)
            last = stub.GetLast(telemetry_pb2.DroneRequest(drone_id='001'), timeout=TIMEOUT)
        except grpc.RpcError as exc:
            print(f'gRPC error: {exc.code()}: {exc.details()}', file=sys.stderr)
            return 1
    print(f'accepted={ack.accepted}, received={ack.received}')
    print(f'last: alt={last.alt} battery={last.battery}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

Кожен виклик має `timeout=5.0`: без deadline клієнт висить, якщо сервер недоступний.

### 6. Запуск

У першому терміналі:

```bash
python server.py
```

У другому:

```bash
python client.py
```

Очікуваний вивід клієнта:

```text
accepted=True, received=5
last: alt=104.0 battery=91
```

## Перевірка

Контракт перевіряється структурно, без мережі й компіляції (команда виконується з теки модуля):

```bash
python checks/check_lab.py --target ~/drone-labs/11-grpc
```

Скрипт читає `telemetry.proto` у теці-аргументі `--target` і вимагає `package`, `service Telemetry`, обидва RPC та поля з правильними типами й тегами. Еталон із репозиторію перевіряється так:

```bash
python checks/check_lab.py --target solution
```

Очікуваний вивід: `PASS: proto містить сервіс, обидва RPC і коректні поля з тегами`.

## Розбір збоїв

- `TypeError: StreamTelemetry() missing 1 required positional argument` — викликали unary-стаб, а RPC client-streaming приймає ітератор: `stub.StreamTelemetry(frames())`.
- `StatusCode.UNAVAILABLE` одразу після старту — сервер не встиг відкрити порт; клієнт має повторювати спробу з backoff, а не висіти без `timeout`.
- `ModuleNotFoundError: telemetry_pb2` — код згенеровано не в тій теці; генерацію виконують із робочої теки (`--python_out=.`), там же запускають сервер і клієнт.
- Перевикористані номери тегів — сумісність ламається: старий клієнт читає нове поле з іншим змістом.

## Очікуваний результат

- `telemetry.proto` з client-streaming і unary RPC.
- `server.py` і `client.py`, що обмінюються потоком кадрів.
- `PASS` від `checks/check_lab.py`.
