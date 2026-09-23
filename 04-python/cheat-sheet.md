# Cheat Sheet 04: Python для телеметрії

- `uvicorn fastapi_telemetry:app --reload` — запуск API
- `curl -X POST localhost:8000/telemetry -H "Content-Type: application/json" -d '{...}'`
- `await asyncio.to_thread(blocking_fn, args)` — безпечний місток
- `asyncio.gather(*tasks, return_exceptions=True)` — масова розсилка
- `pytest -q` і `pytest -k test_name -x`
- `python -c "from main import app; print(app.routes)"` — інвентар маршрутів
