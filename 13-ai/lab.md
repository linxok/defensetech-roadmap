# Лабораторна робота 13: офлайн-генератор місій з валідацією

## Мета

Реалізувати `mission_prompt.py`: генерацію місії у валідовану Pydantic-модель `Mission`, детермінований офлайн-режим без мережі та опційний виклик LLM із таймаутом.

## Передумови

- Python 3.11+ і `pydantic>=2` (встановлюється разом із `fastapi`). Базовий офлайн-режим не потребує ні мережі, ні API-ключа.
- Для LLM-режиму: `openai==1.35.10` і змінна середовища `OPENAI_API_KEY`.

## Кроки

### 1. Робоча тека

```bash
mkdir -p ~/drone-labs/13-mission
cd ~/drone-labs/13-mission
```

### 2. Моделі `Waypoint` і `Mission`

Створіть `mission_prompt.py`. Модель — це контракт безпеки: жоден waypoint не потрапляє далі, якщо не пройшов перевірку діапазонів.

```python
"""Генерація місії з текстового запиту + валідація JSON-схемою."""

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
```

Обмеження: `alt` — від 0 (не включно) до 500 м, широта `±90`, довгота `±180`, у місії 2–100 точок, `seq` — неперервні від 0.

### 3. Офлайн-генератор `offline_mission`

Детермінована survey-сітка в два ряди: працює без мережі й дає однаковий результат на однакових вхідних даних.

```python
def offline_mission(lat: float, lon: float, alt: float, count: int) -> Mission:
    columns = (count + 1) // 2
    step = 0.0002  # ~22 м по широті
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
```

Для `count=5` функція повертає 5 waypoint-ів із `seq` 0–4, координатами в межах 0.01° від центру і `alt`, рівним переданому.

### 4. `generate`: LLM із таймаутом і fallback

```python
PROMPT = (
    'Generate a survey mission as JSON: {"name": str, "waypoints": '
    '[{"seq": int, "lat": float, "lon": float, "alt": float}]}. '
    'Waypoints must be ordered, seq starts at 0, altitude in meters. '
    'Center: lat={lat}, lon={lon}, altitude={alt} m, waypoints: {count}.'
)


def llm_mission(lat: float, lon: float, alt: float, count: int) -> Mission:
    from openai import OpenAI

    client = OpenAI(timeout=30.0)
    response = client.chat.completions.create(
        model=MODEL,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You generate safe UAV survey missions.'},
            {'role': 'user', 'content': PROMPT.format(lat=lat, lon=lon, alt=alt, count=count)},
        ],
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
```

Два принципові моменти: `OpenAI(timeout=30.0)` не дає виклику висіти хвилинами, а `import openai` — усередині `llm_mission`, щоб модуль імпортувався без ключа й без встановленого пакета `openai`. Будь-яка невалідна відповідь моделі замінюється офлайн-місією, а не потрапляє в автопілот.

### 5. CLI

```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lat', type=float, required=True)
    parser.add_argument('--lon', type=float, required=True)
    parser.add_argument('--alt', type=float, default=100.0)
    parser.add_argument('--count', type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mission = generate(args.lat, args.lon, args.alt, args.count)
    print(json.dumps(mission.model_dump(), indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
```

### 6. FastAPI-ендпоінт (опційно)

`generate` — синхронна функція, тому в async-ендпоінті її не можна викликати напряму: блокуючий `client.chat.completions.create` зупинить event loop. Правильно — через `asyncio.to_thread`:

```python
import asyncio

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Prompt(BaseModel):
    lat: float
    lon: float
    alt: float = 100.0
    count: int = 5


@app.post('/generate-mission')
async def generate_mission(prompt: Prompt) -> Mission:
    return await asyncio.to_thread(generate, prompt.lat, prompt.lon, prompt.alt, prompt.count)
```

Альтернатива — `AsyncOpenAI()` з `timeout=30.0` і `await client.chat.completions.create(...)`.

### 7. Запуск

```bash
python mission_prompt.py --lat 50.4501 --lon 30.5234 --alt 100 --count 5
```

Очікуваний вивід (фрагмент):

```json
{
  "name": "survey-5wp",
  "waypoints": [
    {"seq": 0, "lat": 50.4501, "lon": 30.5234, "alt": 100.0},
    {"seq": 1, "lat": 50.4501, "lon": 30.5236, "alt": 100.0}
  ]
}
```

Невалідні дані відхиляються ще до генерації: `Waypoint(seq=0, lat=50.0, lon=30.0, alt=900.0)` кидає `ValidationError` (`alt` більший за 500 м).

## Перевірка

```bash
python checks/check_lab.py --target ~/drone-labs/13-mission
python checks/check_lab.py --target solution
```

Перевірка виконується офлайн: вона прибирає `OPENAI_API_KEY` з середовища й вимагає, щоб `generate` повернув офлайн-місію. Очікуваний вивід: `PASS: місія валідується, офлайн-режим працює`.

## Розбір збоїв

- `OpenAIError: The api_key client option must be set` — клієнт створено на рівні модуля при імпорті; створюйте `OpenAI()` усередині `llm_mission`.
- `generate` без ключа падає з мережевою помилкою — немає перевірки `OPENAI_API_KEY`: перевірка має бути перед викликом, а не в `except`.
- Невалідна відповідь моделі потрапляє в місію — не викликано `Mission.model_validate` або відсутній fallback на `ValidationError`/`json.JSONDecodeError`.
- Async-ендпоінт «зависає» під навантаженням — синхронний виклик у `async def` блокує event loop; потрібен `asyncio.to_thread` або `AsyncOpenAI`.

## Очікуваний результат

- `mission_prompt.py` з `Waypoint`, `Mission`, `offline_mission` і `generate`.
- Приклад JSON місії, згенерований без мережі.
- `PASS` від `checks/check_lab.py` і README з інструкцією.
