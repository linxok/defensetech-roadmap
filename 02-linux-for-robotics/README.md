# 02. Linux для робототехніки

> Статус: outline

Навчитися перетворювати скрипт на керований сервіс: systemd, права доступу, udev, serial, журнали й діагностика на companion-комп’ютері.

## Що потрібно зрозуміти

- systemd керує життєвим циклом процесів: `Restart=on-failure`, залежності `After=`, ізоляція через `User=`, `DeviceAllow=`.
- udev створює стабільні імена пристроїв: `/dev/ttyUSB0` може стати `/dev/ttyFC` за vendor/product ID — це прибирає «порт зник».
- Доступ до serial потребує групи `dialout`; перевірка — `ls -l` і `id`.
- journald збирає stdout/stderr сервісу: `journalctl -u drone-telemetry -f`.
- CAN на Linux — це SocketCAN: `ip link set can0 type can bitrate 500000`, далі робота через сокет як з мережевим інтерфейсом.
- Watchdog і resource limits (`CPUQuota=`, `MemoryMax=`) захищають від зависань на борту.

## Контрольні питання

1. Які директиви unit-файлу роблять сервіс відмовостійким?
2. Як udev-правило прибирає залежність від номера `/dev/ttyUSB*`?
3. Чим `journalctl` кращий за лог у файл на embedded-носії?
4. Як перевірити, що процес справді читає serial, а не мовчки падає?
5. Коли CAN кращий за UART для підключення периферії?

## Очікуваний результат

Працюючий systemd-сервіс `drone-telemetry`, який читає serial, пише в journald і перезапускається при збої (еталон: `solution/`).

## Зв'язок з capstone

Крок 2: контейнеризація вимагає розуміння процесів, сигналів і прав — те саме, що systemd робить на борту, Docker робить у стеку.

## Типові помилки

- Сервіс працює від root без потреби — достатньо `User=dronesvc` і групи `dialout`.
- `Restart=always` без `RestartSec` створює цикл миттєвих перезапусків, який забиває журнал.
- udev-правило без `MODE`/`GROUP` — пристрій знайдено, але доступу немає.
- Забути `daemon-reload` після правки unit-файлу.

## Первинні джерела

- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) — усі директиви unit-файлу
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html) — ізоляція, ліміти, права
- [udev(7)](https://www.freedesktop.org/software/systemd/man/latest/udev.html) — правила та атрибути пристроїв
- [pyserial docs](https://pyserial.readthedocs.io/en/latest/) — читання serial з Python
- [Linux kernel docs](https://www.kernel.org/doc/html/latest/) — драйвери, tty, can

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
