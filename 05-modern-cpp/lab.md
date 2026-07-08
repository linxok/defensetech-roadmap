# Лабораторна робота 05: MAVLink Parser на C++

## Мета

Реалізувати простий парсер MAVLink-повідомлень на C++ з thread-safe чергою.

## Передумови

- C++17
- CMake 3.16+

## Кроки

### 1. Структура

```
include/
  message_queue.hpp
  mavlink_parser.hpp
src/
  main.cpp
  mavlink_parser.cpp
tests/
  test_parser.cpp
CMakeLists.txt
```

### 2. MessageQueue

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

### 3. Збірка

```bash
mkdir build && cd build
cmake ..
make
./parser
```

## Очікуваний результат

- C++ проєкт з CMake.
- Thread-safe черга.
- Тести.
