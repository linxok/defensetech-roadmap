# Demos

Невеликі самостійні демо. Все, що вже покрито модулями курсу, живе
в модулях, а не тут — щоб не дублювати код і контент.

| Демо | Що показує | Куди дивитися за повною версією |
|---|---|---|
| `object-detection/` | YOLO через Ultralytics (інший шлях, ніж OpenCV DNN у курсі) | `12-computer-vision/` |
| `mission-planner/` | мінімальний FastAPI CRUD для місій | `10-backend/lab.md`, `16-projects/02-mission-service...` |

## Видалені як дублікати

- `full-stack-telemetry/` → переїхав у `capstone/` і розширений
  (sim/SITL, тести, метрики).
- `telemetry-demo/` → замінено на `capstone/`.
- `ai-mission-generator/` → замінено на `13-ai/solution/mission_prompt.py`
  (валідація схеми, офлайн-fallback).
- `flight-log-analyzer/` → замінено на `08-px4/solution/` і мініпроєкт
  «Flight Log Analyzer» у `08-px4/mini-project.md`.

## Запуск

Кожне демо має власний `README.md` і `requirements.txt`:

```bash
cd demos/object-detection
pip install -r requirements.txt
python detect.py --help
```
