"""Спрощена демонстрація офлайн-генерації місії: Pydantic-валідація без мережі.

Показує мінімум: моделі з обмеженнями та детермінований генератор.
Повна версія з LLM, таймаутом і fallback — у `solution/mission_prompt.py`.

Запуск:

    python mission_prompt.py --lat 50.4501 --lon 30.5234 --alt 100 --count 5
"""

from __future__ import annotations

import argparse
import json

from pydantic import BaseModel, Field, field_validator

STEP = 0.0002  # ~22 м по широті


class Waypoint(BaseModel):
    seq: int = Field(ge=0)
    lat: float = Field(ge=-90.0, le=90.0)
    lon: float = Field(ge=-180.0, le=180.0)
    alt: float = Field(gt=0.0, le=500.0)


class Mission(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    waypoints: list[Waypoint]

    @field_validator('waypoints')
    @classmethod
    def validate_waypoints(cls, value: list[Waypoint]) -> list[Waypoint]:
        if not 2 <= len(value) <= 100:
            raise ValueError('mission must have 2..100 waypoints')
        if [w.seq for w in value] != list(range(len(value))):
            raise ValueError('seq must be contiguous starting at 0')
        return value


def offline_mission(lat: float, lon: float, alt: float, count: int) -> Mission:
    """Найпростіша детермінована місія: точки вздовж паралелі."""
    waypoints = [
        Waypoint(seq=index, lat=lat, lon=round(lon + STEP * index, 6), alt=alt)
        for index in range(count)
    ]
    return Mission(name=f'offline-{count}wp', waypoints=waypoints)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--alt', type=float, default=100.0)
    parser.add_argument('--count', type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mission = offline_mission(args.lat, args.lon, args.alt, args.count)
    print(json.dumps(mission.model_dump(), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
