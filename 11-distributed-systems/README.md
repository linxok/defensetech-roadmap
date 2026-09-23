# 11. Розподілені системи

> Статус: outline

Зрозібрати gRPC/Protobuf, Kafka і DDS: коли вони потрібні флоту дронів і які гарантії дають.

## Що потрібно зрозуміти

- gRPC: контракт у `.proto`, чотири типи RPC (unary, server/client streaming, bidirectional), HTTP/2 і кодогенерація для багатьох мов.
- Protobuf: бінарний, компактний, зворотно сумісний за додавання полів; номери тегів — контракт, їх не можна перевикористовувати.
- Kafka: append-only лог, партиції дають порядок у межах ключа (наприклад, `drone_id`), retention за часом/розміром.
- DDS: peer-to-peer pub/sub, QoS-політики; основа ROS2 і реального часу, де затримка важливіша за строгий порядок.
- Флот — це розподілена система: часткові відмови неминучі, треба проєктувати retry, idempotency і backpressure.
- CAP-компроміс: у телеметрії обирають availability, у командах — consistency (підтверджений стан автопілота).
- Service mesh і sidecar-проксі дають mTLS, retries і telemetry без зміни коду сервісів — ціна — складність експлуатації.

## Контрольні питання

1. Коли gRPC кращий за REST для флоту?
2. Як Kafka зберігає порядок повідомлень одного дрона?
3. Чим DDS-модель відрізняється від брокерної?
4. Що тільки й може гарантувати at-least-once?
5. Коли service mesh — передчасна складність?

## Очікуваний результат

Скомпільований gRPC-контракт і клієнт (`solution/telemetry.proto`) + таблиця порівняння транспортів.

## Зв'язок з capstone

Крок 11: при зростанні флоту capstone може перейти з HTTP на gRPC або Kafka — рішення задокументувати.

## Типові помилки

- Перевикористати номери тегів protobuf — ламає сумісність
- Kafka з одним partition на всі дрони — втрата паралелізму
- gRPC без deadline — зависання клієнта
- Mesh заради mesh без SLO і команди, що вміє його експлуатувати

## Первинні джерела

- [gRPC concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) — RPC і стрімінг
- [Protocol Buffers](https://protobuf.dev/programming-guides/proto3/) — proto3, теги, сумісність
- [Kafka documentation](https://kafka.apache.org/documentation/) — партиції, retention
- [DDS specification](https://www.omg.org/spec/DDS/) — QoS-модель
- [CycloneDDS](https://cyclonedds.io/docs/cyclonedds/latest/) — реалізація DDS

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
