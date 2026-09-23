# Приклади 05: Сучасний C++

У `examples/` — спрощений self-contained thread pool (`thread_pool.cpp`)
і CMake-збірка зі стандартом C++20 та `-Wall -Wextra -Werror`. Повне
рішення лабораторної (thread pool із futures + MAVLink-парсер із
known-answer CRC-тестом) — у `solution/`.

Збірка і запуск прикладу:

```bash
cmake -S 05-modern-cpp/examples -B 05-modern-cpp/examples/build
cmake --build 05-modern-cpp/examples/build
./05-modern-cpp/examples/build/thread_pool
```

Або без CMake:

```bash
g++ -std=c++20 -Wall -Wextra -Werror -pthread \
  05-modern-cpp/examples/thread_pool.cpp -o /tmp/thread_pool && /tmp/thread_pool
```

Перевірка рішення лабораторної:

```bash
python 05-modern-cpp/checks/check_lab.py --target 05-modern-cpp/solution
```
