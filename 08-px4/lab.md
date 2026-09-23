# Лабораторна робота 08: Менеджер параметрів PX4

## Мета

Побудувати CLI `px4_param.py` для читання і зміни параметрів PX4 через MAVSDK.

## Передумови

- Python 3.11+ і venv:

```bash
python3 -m venv px4-lab
source px4-lab/bin/activate
pip install mavsdk
```

- PX4 SITL (jMAVSim знято в PX4 ≥1.15, тому використовується gz):

```bash
make px4_sitl gz_x500
```

MAVSDK підключається до `udp://:14540`. Для автоматичної перевірки SITL не потрібен — `checks/check_lab.py` тестує чисті функції та CLI офлайн.

## Контракт

Створіть у своїй робочій теці файл `px4_param.py` з функціями:

- `validate_name(name: str) -> str` — імʼя параметра має відповідати `^[A-Z][A-Z0-9_]{0,15}$`; невалідне (нижній регістр, дефіс, довше 16 символів, порожнє) кидає `SystemExit`;
- `format_param(name, value) -> str` — `'<NAME> = <value>'`, значення у форматі `:.6g`; `format_param('MPC_XY_P', 0.85)` дає `'MPC_XY_P = 0.85'`;
- `format_params(params) -> list[str]` — приймає послідовність обʼєктів з атрибутами `.name` і `.value` (у перевірці це `namedtuple('Param', 'name value')`), сортує за `.name` і форматує кожен; `format_params([Param('B_PARAM', 2.0), Param('A_PARAM', 1.0)])` дає `['A_PARAM = 1', 'B_PARAM = 2']`;
- `parse_args(argv=None)` — CLI з підкомандами:
  - `get NAME` — прочитати один параметр;
  - `set NAME VALUE` — записати (`VALUE` конвертується у `float`);
  - `list [PREFIX]` — вивести параметри за префіксом;
  - після `parse_args(['get', 'MPC_XY_P'])` має бути `command == 'get'` і `name == 'MPC_XY_P'`.

Додатково `python px4_param.py --help` мусить завершуватися з кодом 0.

## Кроки

### 1. Чисті функції

```python
import re

PARAM_RE = re.compile(r'^[A-Z][A-Z0-9_]{0,15}$')


def validate_name(name):
    if not PARAM_RE.match(name):
        raise SystemExit(f'invalid PX4 parameter name: {name!r}')
    return name


def format_param(name, value):
    return f'{validate_name(name)} = {value:.6g}'


def format_params(params):
    return [
        format_param(param.name, param.value)
        for param in sorted(params, key=lambda item: item.name)
    ]
```

### 2. CLI

```python
import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='PX4 parameter manager')
    sub = parser.add_subparsers(dest='command', required=True)

    get = sub.add_parser('get', help='read one parameter')
    get.add_argument('name')

    set_ = sub.add_parser('set', help='write one parameter')
    set_.add_argument('name')
    set_.add_argument('value', type=float)

    list_ = sub.add_parser('list', help='list parameters by prefix')
    list_.add_argument('prefix', nargs='?', default='')
    return parser.parse_args(argv)
```

### 3. Робота з MAVSDK

```python
from mavsdk import System


async def connect(address='udp://:14540'):
    drone = System()
    await drone.connect(system_address=address)
    async for state in drone.core.connection_state():
        if state.is_connected:
            return drone
    raise TimeoutError(f'no PX4 connection at {address}')
```

`get` викликає `drone.param.get_param_float(name)`, `set` — `drone.param.set_param_float(name, value)`, `list` перебирає `drone.param.get_all_params()` і друкує ті, що починаються з префікса. Імʼя перед викликом MAVSDK проганяйте через `validate_name`, кожен виклик обгортайте в `asyncio.wait_for(..., timeout=10)`, а `main()` запускайте через `asyncio.run()` лише під `if __name__ == '__main__':`.

```python
async def run(args):
    drone = await asyncio.wait_for(connect('udp://:14540'), timeout=30)
    if args.command == 'get':
        value = await asyncio.wait_for(drone.param.get_param_float(args.name), timeout=10)
        print(format_param(args.name, value))
    elif args.command == 'set':
        await asyncio.wait_for(drone.param.set_param_float(args.name, args.value), timeout=10)
        print(f'{args.name} := {args.value}')
    else:
        async for param in drone.param.get_all_params():
            if str(param.name).startswith(args.prefix):
                print(format_param(str(param.name), float(param.value)))
    return 0
```

### 4. Приклади запуску

```bash
python px4_param.py list MPC_XY
python px4_param.py get MPC_XY_VEL_MAX
python px4_param.py set MPC_XY_VEL_MAX 12.5
python px4_param.py get MPC_XY_VEL_MAX
```

Очікуваний вивід для читання:

```text
$ python px4_param.py get MPC_XY_VEL_MAX
MPC_XY_VEL_MAX = 12
```

## Перевірка

Якщо `px4_param.py` лежить поряд із цим `lab.md`, запускайте з теки модуля:

```bash
python checks/check_lab.py --target .
```

Для файлу в іншій теці вкажіть її: `python checks/check_lab.py --target ~/px4-lab`.

Скрипт імпортує `px4_param.py` з цільової теки, перевіряє `validate_name` (валідне імʼя і чотири невалідні), `format_param`, сортування у `format_params`, розбір `get MPC_XY_P` і `--help` з кодом 0. SITL для цього не потрібен. Для еталона — `--target solution`.

## Очікуваний результат

- `px4_param.py get/set/list` працює з PX4 SITL.
- Невалідні імена параметрів відхиляються з `SystemExit`.
- `checks/check_lab.py --target .` завершується з кодом 0.

## Розбір збоїв

- `FAIL: у модулі немає validate_name` — функції названо інакше або вони загублені в класі.
- `FAIL: невалідне імʼя ... не відхилено` — regex не покриває регістр, дефіс або довжину; невалідне імʼя мусить кидати саме `SystemExit`.
- `--help` завершується не з 0 — `asyncio.run(main())` викликається на рівні модуля; перенесіть під `if __name__ == '__main__':`.
- `no PX4 connection` — SITL не запущено або адреса інша ніж `udp://:14540`.
- Параметр типу `int` зіпсовано через `set_param_float` — перевіряйте тип перед записом.
