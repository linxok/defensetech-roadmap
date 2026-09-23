# Лабораторна робота 05: MAVLink Parser на C++

## Мета

Реалізувати thread pool із чергою задач і парсер MAVLink v2-фреймів із
CRC-перевіркою так, щоб усе компілювалося без попереджень під C++20.

## Передумови

- C++20-компілятор (`g++` або `clang++`) — потрібні `std::bind_front`, `std::span`.
- CMake 3.16+ — опційно: `checks/check_lab.py` компілює файли напряму.

## Кроки

### 1. Файли здачі

Перевірка очікує в теці здачі рівно ці чотири файли:

```text
thread_pool.cpp
parser.hpp
parser.cpp
parser_test.cpp
```

### 2. Черга задач

Основа `thread_pool.cpp` — thread-safe черга:

```cpp
#include <queue>
#include <mutex>
#include <condition_variable>

template <typename T>
class MessageQueue {
    std::queue<T> q_;
    std::mutex m_;
    std::condition_variable cv_;
public:
    void push(T value) {
        std::lock_guard<std::mutex> lock(m_);
        q_.push(std::move(value));
        cv_.notify_one();
    }
    T pop() {
        std::unique_lock<std::mutex> lock(m_);
        cv_.wait(lock, [this] { return !q_.empty(); });
        T value = std::move(q_.front());
        q_.pop();
        return value;
    }
};
```

### 3. ThreadPool

Додайте в `thread_pool.cpp` клас `ThreadPool`:

- конструктор `ThreadPool(std::size_t)` піднімає N воркерів (`ThreadPool(4)` у `main`);
- `submit(fn, args...)` повертає `std::future` результату — через `std::packaged_task` і `std::bind_front`;
- деструктор виставляє `stopping_`, викликає `ready_.notify_all()` і `join()` для кожного воркера;
- воркер бере задачі з черги; при `stopping_` та порожній черзі — вихід.

У `main()`:

1. створіть `ThreadPool pool(4)`;
2. для `i` від 1 до 8 надішліть задачу, що повертає `i * i` (затримка 50 мс, як в еталоні);
3. дочекайтеся `future.get()` і надрукуйте `tasks=8 sum_of_squares=204`;
4. поверніть 0, якщо сума — 204, інакше 1.

### 4. Парсер

`parser.hpp` оголошує інтерфейс (ті самі імена використовує тест):

```cpp
namespace mavlink {

inline constexpr std::uint8_t kMagicV2 = 0xFD;

struct Frame {
    std::uint8_t sequence{};
    std::uint8_t system_id{};
    std::uint8_t component_id{};
    std::uint32_t message_id{};
    std::vector<std::uint8_t> payload;
    bool signed_frame{};
};

std::uint16_t x25_crc(std::span<const std::uint8_t> data, std::uint16_t crc = 0xFFFF);
std::uint16_t frame_crc(std::span<const std::uint8_t> frame, std::uint8_t crc_extra);
std::optional<Frame> parse_header(std::span<const std::uint8_t> bytes);
bool checksum_valid(std::span<const std::uint8_t> frame, std::uint8_t crc_extra);
std::size_t frame_size(std::span<const std::uint8_t> bytes);

}  // namespace mavlink
```

Правила формату:

- заголовок — 10 байт: `0xFD`, payload length, incompat flags, compat flags, seq, sysid, compid, 24-бітний msgid (little-endian);
- `frame_size` = 10 + payload length + 2 (+13, якщо виставлений біт підпису `0x01`);
- `frame_crc` вважає CRC-16/MCRF4XX від байтів `[1, 10 + payload length)` і додає `crc_extra`;
- `parse_header` перевіряє magic і повну довжину; `checksum_valid` порівнює порахований CRC із двома байтами у фреймі.

### 5. Known-answer тест

`parser_test.cpp` мусить містити обидві перевірки:

- синтетичний фрейм: seq=42, sysid=7, compid=1, msgid=33, payload `{0x01, 0x02, 0x03}`, `crc_extra=104` — `checksum_valid` із 104 → true, із 105 → false; пошкоджений байт і bad magic → false;
- еталонний 40-байтний фрейм `GLOBAL_POSITION_INT` (msgid=33, `crc_extra=104`), згенерований pymavlink:

```text
0xfd, 0x1c, 0x00, 0x00, 0x2a, 0x07, 0x01, 0x21, 0x00, 0x00, 0xe8, 0x03,
0x00, 0x00, 0x08, 0x13, 0x12, 0x1e, 0x50, 0x80, 0x31, 0x12, 0xc0, 0xd4,
0x01, 0x00, 0xa0, 0x86, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x28, 0x23, 0xe3, 0xc3
```

Для нього: `checksum_valid(frame, 104)` → true, `checksum_valid(frame, 105)` → false,
`parse_header` дає msgid=33, seq=42, sysid=7, compid=1, payload 28 байт; на кінець — вивід
`parser tests passed` і код 0.

### 6. Компіляція і прогін

```bash
g++ -std=c++20 -Wall -Wextra -Werror -pthread thread_pool.cpp -o thread_pool
./thread_pool

g++ -std=c++20 -Wall -Wextra -Werror -I. parser_test.cpp parser.cpp -o parser_test
./parser_test
```

## Перевірка

```bash
python 05-modern-cpp/checks/check_lab.py --target 05-modern-cpp/solution
python 05-modern-cpp/checks/check_lab.py --target <тека з чотирма файлами>
```

Скрипт компілює `thread_pool.cpp` з `-std=c++20 -Wall -Wextra -Werror -pthread`,
а `parser_test.cpp + parser.cpp` — з `-I <тека>`, тому будь-який warning валить перевірку.

## Розбір збоїв

- Забутий `-pthread` — помилка лінкування.
- CRC рахується від magic-байта — known-answer тест не проходить.
- Пул без `stopping_` зависає на виході або падає в деструкторі.
- `parser.hpp` не знайдено — компілюйте тест із `-I.` (тека здачі).
- Warning перетворення типів під `-Werror` — додайте явні `static_cast`.

## Очікуваний результат

- Чотири файли, що компілюються без попереджень під C++20.
- `thread_pool` друкує `tasks=8 sum_of_squares=204` і повертає 0.
- `parser_test` проходить known-answer CRC-перевірку на фреймі з pymavlink.
