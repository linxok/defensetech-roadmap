# Приклади 03: Мережі для робототехніки

У `examples/` — UDP-клієнт для перевірки моста і MQTT-підписник.

## UDP-клієнт

`udp_client.py` надсилає один коректний JSON-пакет і один битий, щоб перевірити валідацію. Міст не відповідає на UDP, тому читання відповіді обмежено таймаутом, а не вічним блокуванням.

```bash
python -m pip install websockets
python solution/udp_ws_bridge.py --udp-port 14550 --ws-port 8765
python examples/udp_client.py --host 127.0.0.1 --port 14550
```

Битий пакет має дати `warning` у журналі моста, а валідний — дійти до WebSocket-клієнтів.

## MQTT-підписник

`mqtt_sub.py` потребує локального брокера (наприклад, Mosquitto) і пакета `paho-mqtt`:

```bash
python -m pip install paho-mqtt
mosquitto -v
python examples/mqtt_sub.py
```

Повний міст дивіться в `solution/udp_ws_bridge.py`.
