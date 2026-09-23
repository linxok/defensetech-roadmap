# 05. Сучасний C++

> Статус: complete

C++20 як інструмент гарячих шляхів телеметрії: RAII, безпечне володіння, thread pool і парсер MAVLink v2 із CRC-перевіркою. Модуль вчить писати код, що компілюється під `-Wall -Wextra -Werror` без жодного попередження, і доводити його known-answer тестами. Це відповідь на питання «що робити, коли Python-обробник перестає тримати потік на 5–10 тисячах повідомлень за секунду».

## Що потрібно зрозуміти

### Володіння і RAII

- Ресурс належить об’єкту: `std::unique_ptr` для пам’яті, `std::lock_guard`/`std::unique_lock` для м’ютекса, `std::jthread` для потоку, який сам приєднується в деструкторі.
- Деструктор `ThreadPool` — частина контракту: виставити `stopping_`, розбудити воркерів через `ready_.notify_all()` і викликати `join()`, інакше програма або вішає CI, або падає на виході.
- Копіювання — витрата; у гарячому шляху приймайте `std::span` і `std::string_view` (невласні view), а володіючий `std::vector` наповнюйте через `reserve()`.
- `std::span` не подовжує життя буфера: якщо `Frame` зберігає view на тимчасовий масив, отримаєте use-after-free; володіючі дані копіюються у `std::vector`.

### Паралелізм

- Thread pool = черга задач + N воркерів + умовна змінна: `push` під `std::lock_guard`, `pop` під `std::unique_lock` із предикатом на непорожню чергу.
- `std::packaged_task` загортає виклик і віддає `std::future` з результатом та винятком; `std::bind_front(fn, args...)` фіксує аргументи без ручних лямбд.
- `submit` у зупинений пул не має приймати задачу мовчки: знищена невиконана задача дасть `Broken promise` у `future.get()`.
- `-fsanitize=thread` (TSan) ловить гонки на даних, `-fsanitize=address,undefined` — вихід за межі й UB; санітайзери вмикають у тестовій збірці, а не в релізі.

### Парсер MAVLink v2

- Кадр починається з `0xFD`; далі payload length (0–255), incompat/compat flags, sequence, system/component id, 24-бітний message id (little-endian), payload і 2 байти CRC. Біт `0x01` у incompat flags означає підпис, який додає ще 13 байт.
- `parse_header` працює зі `std::span<const std::uint8_t>`: перевіряє magic і повну довжину, повертає `std::optional<Frame>`; читання — лише через `.subspan`, жодного виходу за межі буфера.
- Payload length у кадрі — це довжина після відкидання хвостових нулів, тому вона не дорівнює `sizeof` повідомлення: парсер має дозаповнити решту нулями, а не довіряти довжині.
- CRC MAVLink — CRC-16/MCRF4XX: init `0xFFFF`, відображений поліном `0x8408`, XOR-out `0x0000`; контрольне значення для рядка `123456789` — `0x6F91`.
- CRC покриває байти `frame[1, 10 + payload_len)` (без magic) і завершується байтом `crc_extra` конкретного message id; сам CRC записується little-endian.
- `crc_extra` береться зі згенерованих заголовків (для `GLOBAL_POSITION_INT` — 104); парсер без нього приймає випадково валідні кадри.
- `checksum_valid(frame, crc_extra)` і `frame_size(bytes)` тримають логіку чистою: розмір — `10 + payload_len + 2` (+13 за наявності підпису); це звіряється на еталонному 40-байтному кадрі з `lab.md`.

### Збірка

- `g++ -std=c++20 -Wall -Wextra -Werror -pthread` — мінімум для здачі; `-Werror` перетворює попередження перетворень на помилки, поки вони ще дешеві.
- CMake 3.16+ потрібен для великого проєкту: ціль із `target_compile_features(... cxx_std_20)` і окрема тестова ціль із санітайзерами; лабораторна перевірка компілює файли напряму.
- `std::bind_front`, `std::span`, `std::jthread` — саме ті можливості, які вимагають компілятора з повною підтримкою C++20.

## Контрольні питання

1. Який рядок доводить, що всі 8 задач пулу виконані й сума правильна, і який код виходу при цьому очікується?
2. Скільки байтів має кадр MAVLink v2 із payload 28 байт без підпису і скільки — з підписом?
3. Чому `checksum_valid(frame, 104) == true`, а `checksum_valid(frame, 105) == false` на еталонному кадрі `GLOBAL_POSITION_INT`?
4. Яке контрольне значення дає реалізація CRC-16/MCRF4XX для рядка `123456789`?
5. Що побачить `future.get()`, якщо `std::packaged_task` знищено, не виконавши?
6. Чому `std::span` у сигнатурах парсера не рятує від use-after-free і як цього уникнути?
7. Яке повідомлення компілятора з’явиться без `-std=c++20`, а яке — без `#include <functional>`?

## Очікуваний результат

- Чотири файли (`thread_pool.cpp`, `parser.hpp`, `parser.cpp`, `parser_test.cpp`), що компілюються під C++20 без попереджень.
- `thread_pool` друкує `tasks=8 sum_of_squares=204` і повертає 0; `parser_test` друкує `parser tests passed` і повертає 0.
- Пройдений `python 05-modern-cpp/checks/check_lab.py --target <тека>` на власній реалізації.
- Виміряна пропускна здатність парсера на синтетичному потоці (кадрів/с) — цифра для портфоліо.

## Зв'язок з capstone

Розділ «Швидкий старт (режим sim)» у `capstone/README.md` фіксує 5 кадрів/с — це межа Python-обробника, який ви вже вмієте писати. Коли профіль показує десятки тисяч повідомлень за секунду, гарячий шлях (розбір, CRC, агрегація) виносять у C++-сервіс, а результат міряють метриками з розділу «Метрики для портфоліо» — p95 затримки й кадри/с.

## Типові помилки

- `error: ‘span’ is not a member of ‘std’` — компіляція без `-std=c++20` (або старіший стандарт у CMake).
- `error: ‘bind_front’ is not a member of ‘std’; did you forget to ‘#include <functional>’?` — пропущений заголовок.
- `undefined reference to 'pthread_create'` — забутий `-pthread` при лінкуванні.
- `terminate called after throwing an instance of 'std::future_error' what(): Broken promise` — задача знищена без виконання (найчастіше — submit у пул, що вже зупиняється).
- `error: variable ‘crc’ set but not used [-Werror=unused-but-set-variable]` — CRC пораховано, але результат не порівняно з кадром.
- `ERROR: AddressSanitizer: stack-use-after-return` — `std::span` або `std::string_view` пережив буфер, на який вказував.
- Known-answer тест не проходить: `checksum_valid` хибний, якщо CRC раховано від magic-байта або без `crc_extra`.

## Первинні джерела

- [cppreference: std::span](https://en.cppreference.com/w/cpp/container/span) — невласні view, `subspan`, лайфтайм буфера.
- [cppreference: std::bind_front](https://en.cppreference.com/w/cpp/utility/functional/bind_front) — фіксація аргументів для `packaged_task`.
- [cppreference: std::packaged_task](https://en.cppreference.com/w/cpp/thread/packaged_task) — зв’язок задачі з `std::future`.
- [cppreference: std::jthread](https://en.cppreference.com/w/cpp/thread/jthread) — автоприєднання і `stop_token`.
- [C++ Core Guidelines: RAII](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rr-raii) — володіння ресурсами без ручного звільнення.
- [GCC: Warning Options](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html) — `-Wall`, `-Wextra`, `-Werror`, діагностика.
- [MAVLink: Serialization](https://mavlink.io/en/guide/serialization.html) — порядок байтів кадру, CRC, `crc_extra`.
- [mavlink/c_library_v2: checksum.c](https://github.com/mavlink/c_library_v2/blob/master/checksum.c) — еталонна реалізація CRC для звірки.

## Куди далі

Лабораторна: `lab.md`; потім `detailed-guide.md`, `practice.md` і `checklist.md`. Далі за треком — модуль `07-ardupilot` (керування польотом) і `06-mavlink` (діалекти й підпис), якщо потрібен повний протокол, а не лише парсер.
