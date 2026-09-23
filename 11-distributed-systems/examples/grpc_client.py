"""Приклад gRPC-клієнта до контракту `solution/telemetry.proto`.

Підготовка (з кореня модуля, у venv з `grpcio-tools`, див. lab.md):

    python -m grpc_tools.protoc -I solution --python_out=examples --grpc_python_out=examples solution/telemetry.proto

Запуск (поруч має слухати сервер із lab.md):

    python examples/grpc_client.py
"""

from __future__ import annotations

import sys
from collections.abc import Iterator

import grpc

import telemetry_pb2
import telemetry_pb2_grpc

TIMEOUT = 5.0


def frames(count: int = 5) -> Iterator[telemetry_pb2.TelemetryFrame]:
    for seq in range(count):
        yield telemetry_pb2.TelemetryFrame(
            drone_id='001',
            timestamp_ms=1_700_000_000_000 + seq,
            lat=50.4501,
            lon=30.5234,
            alt=100.0 + seq,
            battery=95 - seq,
        )


def main() -> int:
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
