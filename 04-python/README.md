# 04. Python для телеметрії

> Статус: complete

Типізований FastAPI-сервіс телеметрії: приймає вимірювання, валідує фізичні межі полів і віддає останній стан кожного дрона. Головна навичка — поєднувати async-код із синхронними бібліотеками (`pymavlink`, `pika`) через `asyncio.to_thread`, не зупиняючи event loop. Коди відповіді (201 Created / 404 / 422) тут є частиною контракту, і `TestClient` перевіряє їх без запуску сервера. Це прямий прототип backend-компонента capstone.

## Що потрібно зрозуміти

### Модель як контракт

- Pydantic v2 перетворює декларацію полів на перевірку входу: `Field(ge=-90.0, le=90.0)` для `lat`, `ge=0, le=100` для `battery`, `min_length=1, max_length=64` для `drone_id`.
- Порушення обмежень — це не виняток у коді, а 422 Unprocessable Entity зі списком `detail`: `{"type": "less_than_equal", "loc": ["body", "battery"], "msg": "Input should be less than or equal to 100"}`.
- Коди відповіді фіксують семантику: 201 Created — запис прийнято; 200 — читання; 404 — для дрона немає даних; 422 — тіло не пройшло валідацію; 500 не використовується для очікуваних користувацьких помилок.
- Схема відповіді має бути явною (`response_model` або типізоване повернення), інакше сервіс випадково віддає клієнту внутрішній стан сховища.
- 400 Bad Request і 422 — різні речі: 400 означає зламаний JSON, а 422 — синтаксично валідне тіло, яке не пройшло семантичні обмеження; змішування цих кодів заплутує клієнта.
- Один обробник — одна відповідальність: перевірка вхідних даних живе в моделі, доступ до даних — у `TelemetryStore`, формат відповіді — у типі повернення; `if battery > 100` в обробнику — ознака, що межа не на своєму місці.

### asyncio і блокуючі виклики

- `await asyncio.to_thread(func, *args)` — штатний місток до синхронного I/O; саме так викликають `recv_match(blocking=True, timeout=1.0)` і `pika.BlockingConnection`.
- Виклик `connection.recv_match(...)` прямо в корутині заморожує loop на весь таймаут: інші HTTP-запити в цей час не обслуговуються.
- `asyncio.gather(..., return_exceptions=True)` доводить розсилку до кінця, навіть якщо один клієнт відпав; `asyncio.wait` приймає лише задачі (`asyncio.Task`), передача корутин заборонена з Python 3.11.
- `asyncio.TaskGroup` (Python 3.11+) скасовує решту задач при першій помилці — доречний там, де часткова робота неприпустима.
- Таймаут обов’язковий: `asyncio.wait_for(..., timeout=30)` або `timeout` у самому виклику, інакше зависла операція тримає сервіс назавжди.

### Тестування як контракт

- `TestClient(app)` використовується як контекстний менеджер: вхід у `with` виконує startup (`lifespan`), вихід — shutdown; без `with` ресурси можуть не створитися, і тест проходить хибно.
- `pytest.mark.parametrize` покриває межі одним списком пар `(field, bad_value)`; перевіряється код відповіді (≥400), а не текст повідомлення, тому рефакторинг `detail` не ламає тест.
- Фікстура з клієнтом і фабрика валідного payload роблять тести незалежними від порядку та від стану між запусками.
- Тест на 404 цінніший за тест на 200: він доводить, що «дрона немає» відрізняється від «є запис із порожніми полями».
- Тест на 422 документує контракт: кожне нове обмеження моделі має власний негативний кейс, інакше межа неперевірена.

### Ресурси, залежності, сховище

- `requirements.txt` фіксує `fastapi==0.111.0`, `uvicorn[standard]==0.30.0`, `pymavlink==2.4.41`, `pika==1.3.2`; тестові залежності (`httpx`, `pytest`) живуть окремо.
- Підключення до RabbitMQ/БД створюють у `lifespan` FastAPI 0.111 і закривають на зупинці; імпорт модуля не має жодних побічних ефектів.
- Сховище ховається за вузьким інтерфейсом `TelemetryStore: put/get/all`; під ним може бути dict із `threading.Lock` або PostgreSQL — обробники цього не помічають.
- Логи з `drone_id` і кодами відповіді дешевші за дебаг: питання «куди подівся кадр» закривається одним `grep`.
- `GET /health` з кількістю дронів у сховищі — найдешевша перевірка живості для liveness probe в compose чи Kubernetes.
- Сервіс запускається як `uvicorn main:app --reload`, а перевіряється спочатку curl-ом (201/404/422), і лише потім — тестами; це економить хвилини на кожній зміні схеми.

## Контрольні питання

1. Яке тіло і код відповіді повертає `POST /telemetry` на `battery=150`, і який тип помилки вказано в `detail`?
2. Що станеться з паралельними запитами, якщо викликати `recv_match(blocking=True)` без `asyncio.to_thread`?
3. Які коди відповіді перевіряє `04-python/checks/check_lab.py` і на яких саме даних?
4. Чому `asyncio.gather(..., return_exceptions=True)` безпечніший за звичайний `gather` для розсилки телеметрії?
5. Навіщо обмеження `le=100` на `battery` описувати в моделі, а не перевіркою в обробнику?
6. Що зміниться в обробниках, якщо `TelemetryStore` замінити на PostgreSQL, і що для цього має залишитися незмінним?
7. Чому `BlockingConnection`, створений на етапі імпорту, ламає і сервіс, і тести?
8. Який код відповіді отримає клієнт зі зламаним JSON і чим він відрізняється від 422 на семантично невалідному тілі?

## Очікуваний результат

- Робочий `main.py` з моделлю `Telemetry`, сховищем `TelemetryStore` і endpoints `POST /telemetry`, `GET /telemetry/{drone_id}`, `GET /health`.
- Пройдений `python 04-python/checks/check_lab.py --target <тека>`: 201 на валідному POST, відмова на `battery=150`, `lat=100.0`, `alt=-1000.0`, 200 і `d1` у відповіді GET, 404 на невідомий id.
- Звичка читати схему 422 і виправляти межу моделі, а не глушити помилку в обробнику.

## Зв'язок з capstone

У `capstone/README.md` рядок `backend/` з таблиці «Архітектура» — нащадок цього модуля, а розділ «Контракт» фіксує `POST /telemetry` → 202 Accepted і `GET /health`. Відмінність одна: capstone публікує кадр у RabbitMQ замість запису в dict, тоді як моделі, валідація та контрактні тести переносяться без змін.

## Типові помилки

- `ModuleNotFoundError: No module named 'fastapi'` — запуск системним інтерпретатором замість активованого venv.
- `RuntimeError: The starlette.testclient module requires the httpx package to be installed...` — `httpx` не потрапив у dev-залежності.
- `TypeError: Field() got an unexpected keyword argument 'pattern'` — залишки Pydantic v1: у v2 регулярка задається як `pattern`, а `regex` прибрано.
- `pika.exceptions.AMQPConnectionError: [Errno 111] Connection refused` під час імпорту — з’єднання створюється поза `lifespan`.
- 422 на валідному POST — у моделі зайве обов’язкове поле або межі вужчі за `lat=50.4501`, `battery=87`.
- `RuntimeError: asyncio.run() cannot be called from a running event loop` — async-функцію викликають із синхронного тесту напряму.

## Первинні джерела

- [Python docs: asyncio.to_thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) — сигнатура і семантика виконання блокуючої функції в потоці.
- [What's New In Python 3.11: asyncio](https://docs.python.org/3/whatsnew/3.11.html#asyncio) — `TaskGroup` і заборона корутин у `asyncio.wait`.
- [Starlette: TestClient](https://www.starlette.io/testclient/) — httpx-клієнт, контекстний менеджер, `lifespan` у тестах.
- [FastAPI: Lifespan Events](https://fastapi.tiangolo.com/advanced/events/) — старт і зупинка ресурсів без застарілого `on_event`.
- [Pydantic: Fields](https://docs.pydantic.dev/latest/concepts/fields/) — `Field(ge/le/pattern)` і режими валідації.
- [pymavlink: mavutil.py](https://github.com/ArduPilot/pymavlink/blob/master/mavutil.py) — `mavlink_connection`, `recv_match`, `wait_heartbeat`.

## Куди далі

Лабораторна: `lab.md` (кроки та розбір збоїв), далі `detailed-guide.md` і `checklist.md`. Для черг, БД та спостережуваності — модуль `10-backend`, для живого MAVLink-джерела — модуль `06-mavlink`.
