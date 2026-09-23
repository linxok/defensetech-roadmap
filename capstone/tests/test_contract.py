"""Контрактні тести capstone: backend-API та мапінг MAVLink → JSON."""

from __future__ import annotations

import json

import gateway as gateway_mod
import main as backend_main
import pytest
from fastapi.testclient import TestClient
from pymavlink.dialects.v20 import ardupilotmega as mavlink

PAYLOAD = {
    'type': 'GLOBAL_POSITION_INT',
    'system_id': 7,
    'lat': 50.4501,
    'lon': 30.5234,
    'alt': 120.0,
}


class FakePublisher:
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.closed = False

    async def connect(self) -> None:
        pass

    async def publish(self, body: bytes) -> None:
        self.messages.append(json.loads(body))

    async def close(self) -> None:
        self.closed = True


@pytest.fixture()
def client():
    publisher = FakePublisher()
    app = backend_main.create_app(publisher=publisher)
    with TestClient(app) as test_client:
        test_client.publisher = publisher  # type: ignore[attr-defined]
        yield test_client


def test_rejects_payload_without_type(client):
    assert client.post('/telemetry', json={'lat': 1.0}).status_code == 422


def test_accepts_and_publishes_telemetry(client):
    response = client.post('/telemetry', json=PAYLOAD)
    assert response.status_code == 202
    assert client.publisher.messages == [PAYLOAD]


def test_health_reports_ws_clients(client):
    assert client.get('/health').json() == {'status': 'ok', 'ws_clients': 0}


def test_websocket_receives_live_telemetry(client):
    with client.websocket_connect('/ws') as websocket:
        assert client.post('/telemetry', json=PAYLOAD).status_code == 202
        assert websocket.receive_json() == PAYLOAD
        assert client.get('/health').json()['ws_clients'] == 1


def _encode(encoder: str, **fields) -> object:
    class Sink:
        def __init__(self) -> None:
            self.buffer = bytearray()

        def write(self, data: bytes) -> None:
            self.buffer.extend(data)

    sink = Sink()
    sender = mavlink.MAVLink(sink, srcSystem=7, srcComponent=1)
    getattr(sender, f'{encoder}_send')(**fields)
    parser = mavlink.MAVLink(None)
    messages = parser.parse_buffer(bytes(sink.buffer)) or []
    assert messages, f'failed to decode {encoder}'
    return messages[0]


def test_maps_global_position_int():
    message = _encode(
        'global_position_int',
        time_boot_ms=1000,
        lat=504501000,
        lon=305234000,
        alt=120000,
        relative_alt=100000,
        vx=0,
        vy=0,
        vz=0,
        hdg=9000,
    )
    payload = gateway_mod.mavlink_to_telemetry(message)
    assert payload is not None
    assert payload['type'] == 'GLOBAL_POSITION_INT'
    assert payload['system_id'] == 7
    assert payload['lat'] == pytest.approx(50.4501, abs=1e-4)
    assert payload['lon'] == pytest.approx(30.5234, abs=1e-4)
    assert payload['alt'] == pytest.approx(120.0, abs=0.01)
    assert payload['heading'] == pytest.approx(90.0, abs=0.01)


def test_maps_sys_status_battery():
    message = _encode(
        'sys_status',
        onboard_control_sensors_present=0,
        onboard_control_sensors_enabled=0,
        onboard_control_sensors_health=0,
        load=250,
        voltage_battery=12400,
        current_battery=-1,
        battery_remaining=87,
        drop_rate_comm=0,
        errors_comm=0,
        errors_count1=0,
        errors_count2=0,
        errors_count3=0,
        errors_count4=0,
    )
    payload = gateway_mod.mavlink_to_telemetry(message)
    assert payload is not None
    assert payload['battery'] == 87
    assert payload['voltage'] == pytest.approx(12.4, abs=0.01)


def test_ignores_untracked_messages():
    message = _encode(
        'heartbeat',
        type=mavlink.MAV_TYPE_QUADROTOR,
        autopilot=mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
        base_mode=0,
        custom_mode=0,
        system_status=mavlink.MAV_STATE_ACTIVE,
    )
    assert gateway_mod.mavlink_to_telemetry(message) is None
