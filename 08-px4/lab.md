# Лабораторна робота 08: Менеджер параметрів PX4

## Мета

Побудувати Python-утиліту для читання і зміни параметрів PX4 через MAVSDK.

## Передумови

- PX4 SITL запущено (`make px4_sitl jmavsim`).
- Встановлено `mavsdk`.

## Кроки

### 1. Підключення

```python
import asyncio
from mavsdk import System

async def main():
    drone = System()
    await drone.connect(system_address='udp://:14540')
    print('Connected')

asyncio.run(main())
```

### 2. Читання параметра

```python
async def get_param(name):
    param = drone.param
    value = await param.get_param_float(name)
    return value
```

### 3. Зміна параметра

```python
async def set_param(name, value):
    param = drone.param
    await param.set_param_float(name, value)
```

### 4. CLI інтерфейс

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--get')
parser.add_argument('--set')
parser.add_argument('--value', type=float)
args = parser.parse_args()
```

### 5. Тестування

```bash
python px4_param.py --get MPC_XY_P
python px4_param.py --set MPC_XY_P --value 0.8
```

## Очікуваний результат

- CLI для управління параметрами PX4.
- Лог змін.
- README з інструкцією.
