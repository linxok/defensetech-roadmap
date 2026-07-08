#include <thread>
#include <vector>
#include <iostream>

int main() {
    std::vector<std::thread> pool;
    for (int i = 0; i < 4; ++i) {
        pool.emplace_back([i] {
            std::cout << "Worker " << i << " running\n";
        });
    }
    for (auto& t : pool) t.join();
    return 0;
}
