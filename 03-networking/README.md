# 03. Мережі для робототехніки

> Статус: outline

Впевнено обирати транспорт для телеметрії та команд: UDP, TCP, MQTT, WebSocket, DDS — і діагностувати проблеми на рівні пакетів.

## Що потрібно зрозуміти

- MAVLink поверх UDP — стандарт для телеметрії: порт 14550 слухає GCS, другий клієнт бере 14551. TCP (5760) дає доставку, але чутливіший до затримок.
- MQTT 5 додає reason codes, shared subscriptions і message expiry; QoS 1 = at least once, QoS 2 = exactly once (дорожче).
- WebSocket (RFC 6455) дає двонаправлений канал поверх HTTP upgrade — саме тому GCS-фронтенди не потребують окремого протоколу.
- DDS (CycloneDDS/FastDDS) — pub/sub без брокера з QoS-політиками; на ньому стоїть ROS2.
- MTU 1500 байт: великі повідомлення фрагментуються, втрата одного фрагмента вбиває весь пакет — тому телеметрію тримають малою.
- Діагностика: `tcpdump -i any udp port 14550 -X` і Wireshark MAVLink dissector.

## Контрольні питання

1. Чому телеметрія MAVLink зазвичай іде через UDP, а не TCP?
2. Що станеться з пакетом 2000 байт при MTU 1500?
3. Чим QoS 1 відрізняється від QoS 2 і коли це важливо?
4. Як WebSocket-з’єднання встановлюється поверх HTTP?
5. Які порти використовують SITL, PX4 і GCS за замовчуванням?

## Очікуваний результат

UDP → WebSocket міст (еталон: `solution/udp_ws_bridge.py`) з валідацією пакетів і метриками помилок.

## Зв'язок з capstone

Крок 3: gateway capstone перетворює UDP-потік MAVLink у HTTP/WebSocket; розуміння транспортів тут критичне.

## Типові помилки

- Слухати 14550 двома процесами: другий не отримає нічого без SO_REUSEPORT.
- Передавати JSON через UDP без перевірки розміру — 1500 байт не межа довіри.
- Вважати MQTT гарантованим при QoS 0 і дивуватися втратам.

## Первинні джерела

- [Beej’s Guide to Network Programming](https://beej.us/guide/bgnet/) — сокети, UDP/TCP, селект і poll
- [RFC 6455: WebSocket](https://datatracker.ietf.org/doc/html/rfc6455) — рукостискання і кадри
- [MQTT 5.0 OASIS Standard](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html) — QoS, retain, session expiry
- [tcpdump man page](https://www.tcpdump.org/manpages/tcpdump.1.html) — фільтри й розбір пакетів
- [Wireshark User Guide](https://www.wireshark.org/docs/wsug_html_chunked/) — аналіз MAVLink/JSON у реальному часі

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
