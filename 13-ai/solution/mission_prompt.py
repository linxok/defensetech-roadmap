"""Генерація місії з текстового запиту + валідація JSON-схемою.

Запуск:

    OPENAI_API_KEY=... python mission_prompt.py \
        --lat 50.4 --lon 30.5 --alt 100 --count 5

Без `OPENAI_API_KEY` використовується офлайн-генератор (survey-сітка) —
це гарантує, що приклад запускається в CI без мережі й ключів.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

MODEL = 'gpt-4o-mini'


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
        seqs = [w.seq for w in value]
        if seqs != list(range(len(value))):
            raise ValueError('seq must be contiguous starting at 0')
        return value


PROMPT = (
    'Generate a survey mission as JSON: {"name": str, "waypoints": '
    '[{"seq": int, "lat": float, "lon": float, "alt": float}]}. '
    'Waypoints must be ordered, seq starts at 0, altitude in meters. '
    'Center: lat={lat}, lon={lon}, altitude={alt} m, waypoints: {count}.'
)


def offline_mission(lat: float, lon: float, alt: float, count: int) -> Mission:
    """Детермінована survey-сітка: 2 ряди по половина точок."""
    columns = (count + 1) // 2
    step = 0.0002  # ~22 m по широті
    waypoints = []
    for row in range(2):
        for column in range(columns):
            if len(waypoints) >= count:
                break
            offset_lat = step * row
            offset_lon = step * (column if row == 0 else columns - 1 - column)
            waypoints.append(
                Waypoint(
                    seq=len(waypoints),
                    lat=round(lat + offset_lat, 6),
                    lon=round(lon + offset_lon, 6),
                    alt=alt,
                )
            )
    return Mission(name=f'survey-{count}wp', waypoints=waypoints)


def llm_mission(lat: float, lon: float, alt: float, count: int) -> Mission:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You generate safe UAV survey missions.'},
            {'role': 'user', 'content': PROMPT.format(lat=lat, lon=lon, alt=alt, count=count)},
        ],
        timeout=30,
    )
    raw: Any = json.loads(response.choices[0].message.content)
    return Mission.model_validate(raw)


def generate(lat: float, lon: float, alt: float, count: int) -> Mission:
    if not os.environ.get('OPENAI_API_KEY'):
        print('OPENAI_API_KEY is not set: using offline generator', file=sys.stderr)
        return offline_mission(lat, lon, alt, count)
    try:
        return llm_mission(lat, lon, alt, count)
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f'LLM answer failed validation ({exc}); falling back offline', file=sys.stderr)
        return offline_mission(lat, lon, alt, count)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--alt', type=float, default=100.0)
    parser.add_argument('--count', type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        mission = generate(args.lat, args.lon, args.alt, args.count)
    except ValidationError as exc:
        print(f'invalid input: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(mission.model_dump(), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
