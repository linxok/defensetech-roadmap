# 05. Сучасний C++

> Статус: complete

Писати C++20-код із RAII, безпечною пам’яттю і справжнім thread pool; реалізувати парсер MAVLink-фреймів із CRC-перевіркою.

## Що потрібно зрозуміти

- RAII: ресурс живе стільки, скільки об’єкт. `std::unique_ptr`, `std::lock_guard`, `std::jthread` прибирають ручне звільнення.
- Thread pool = черга задач + фіксована кількість воркерів. `std::packaged_task` + `std::future` дають результат і винятки.
- MAVLink v2 фрейм: magic `0xFD`, payload length, incompat/compat flags, seq, sysid, compid, 24-бітний msgid, payload, CRC і опційний підпис.
- CRC MAVLink — CRC-16/MCRF4XX; до кадру додається `crc_extra` повідомлення. Парсер без `crc_extra` дає хибні збіги.
- Уникайте копіювання: `std::span`, `std::string_view`, `reserve`, переміщення. Це критично для 5–10 тисяч повідомлень за секунду.
- CMake з `-Wall -Wextra -Werror` ловить більшість пасток до рев’ю; sanitizers (`-fsanitize=address,undefined`) — для тестів.

## Контрольні питання

1. Чому деструктор ThreadPool обов’язково має зупиняти воркерів?
2. Які байти покриває CRC у MAVLink v2 і навіщо `crc_extra`?
3. Чим `std::packaged_task` кращий за простий `std::function`?
4. Як `std::span` допомагає парсеру без копіювання?
5. Що станеться при `submit` у зупинений пул?

## Очікуваний результат

Thread pool і MAVLink-парсер із known-answer CRC-тестом (`solution/thread_pool.cpp`, `solution/parser*.cpp`).

## Зв'язок з capstone

Крок 5: швидкодіючі компоненти capstone (парсинг, обробка кадрів) можна винести в C++-сервіс із тим самим CMake-каркасом.

## Типові помилки

- Забути `stopping_` і `join()` — програма падає на виході або вішає CI.
- Обчислювати CRC від усього кадру разом із заголовком magic — тест не мине.
- Використовувати `std::vector` у гарячому циклі без `reserve`.
- Ігнорувати `-Werror`: попередження перетворень маскують реальні баги.

## Первинні джерела

- [cppreference: Concurrency](https://en.cppreference.com/w/cpp/thread) — thread, mutex, condition_variable, future
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) — RAII, володіння, проєктування
- [CMake Documentation](https://cmake.org/cmake/help/latest/) — цілі, тести, пресети
- [MAVLink Serialization](https://mavlink.io/en/guide/serialization.html) — формат кадру, CRC, crc_extra
- [mavlink/c_library_v2](https://github.com/mavlink/c_library_v2) — згенеровані C-структури для звірки

## Куди далі

Далі: `lab.md` → `detailed-guide.md` → `checklist.md`.
