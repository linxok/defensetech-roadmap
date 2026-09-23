# Приклади 04: Python для телеметрії

У `examples/` — спрощений FastAPI-сервіс, UDP-сервер і клієнт телеметрії
на stdlib. Повне рішення лабораторної з валідацією, lock і 404 —
`solution/main.py`.

Запуск демо-сервісу (з кореня репозиторію):

```bash
pip install -r requirements.txt
cd 04-python/examples
uvicorn fastapi_telemetry:app --reload
```

Клієнт (окремий термінал; сервіс уже запущено, команда з кореня репозиторію):

```bash
python 04-python/examples/telemetry_client.py
```

Перевірка рішення лабораторної:

```bash
python 04-python/checks/check_lab.py --target 04-python/solution
```
