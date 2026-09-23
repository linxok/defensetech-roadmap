# Cheat Sheet 03: Мережі для робототехніки

- `ss -lunp | grep 14550` — хто слухає UDP-порт
- `tcpdump -i any -n udp port 14550 -X` — розбір пакетів
- `python -m http.server 8000` — швидкий HTTP для перевірки мережі
- MQTT: `mosquitto_sub -t "drone/#" -q 1`
- `ip -s link` — статистика інтерфейсу (errors/dropped)
