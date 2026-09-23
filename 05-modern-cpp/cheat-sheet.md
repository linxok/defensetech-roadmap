# Cheat Sheet 05: Сучасний C++

- `g++ -std=c++20 -Wall -Wextra -Werror -pthread main.cpp -o app`
- `cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build`
- `ctest --test-dir build --output-on-failure`
- `std::jthread` + `std::stop_token` для кооперативної зупинки
- `std::span<const uint8_t>` — безкопіювальний доступ до буфера
- `-fsanitize=address,undefined` у тестовій збірці
