"""Чиста логіка ROS2-моста: MAVLink-повідомлення → dict (тестується без ROS2)."""

from __future__ import annotations

from typing import Any

TRACKED_TYPES = {'GLOBAL_POSITION_INT', 'BATTERY_STATUS', 'SYS_STATUS', 'VFR_HUD'}


def mavlink_to_dict(message: Any) -> dict[str, Any] | None:
    """Повертає словник телеметрії для публікації в ROS2-топік."""
    kind = message.get_type()
    if kind not in TRACKED_TYPES:
        return None

    payload: dict[str, Any] = {'type': kind, 'system_id': message.get_srcSystem()}
    if kind == 'GLOBAL_POSITION_INT':
        payload.update(
            lat=message.lat / 1e7,
            lon=message.lon / 1e7,
            alt=message.alt / 1000.0,
            heading=message.hdg / 100.0 if message.hdg != 65535 else None,
        )
    elif kind == 'BATTERY_STATUS':
        payload['battery'] = message.battery_remaining
    elif kind == 'SYS_STATUS':
        payload.update(
            battery=message.battery_remaining,
            voltage=message.voltage_battery / 1000.0,
        )
    elif kind == 'VFR_HUD':
        payload.update(
            airspeed=message.airspeed,
            groundspeed=message.groundspeed,
            alt=message.alt,
            climb=message.climb,
        )
    return payload
