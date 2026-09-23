// Спрощена демонстрація: черга задач і фіксована кількість воркерів.
// Без std::future і packaged_task — лише механіка черги та коректне
// завершення. Повна версія з futures — у solution/thread_pool.cpp.
// Збірка: cmake -S . -B build && cmake --build build
// Запуск: ./build/thread_pool

#include <condition_variable>
#include <cstddef>
#include <functional>
#include <iostream>
#include <mutex>
#include <queue>
#include <thread>
#include <utility>
#include <vector>

class SimplePool {
public:
    explicit SimplePool(std::size_t worker_count) {
        workers_.reserve(worker_count);
        for (std::size_t i = 0; i < worker_count; ++i) {
            workers_.emplace_back([this] { worker_loop(); });
        }
    }

    ~SimplePool() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            stopping_ = true;
        }
        ready_.notify_all();
        for (auto& worker : workers_) {
            worker.join();
        }
    }

    SimplePool(const SimplePool&) = delete;
    SimplePool& operator=(const SimplePool&) = delete;

    void post(std::function<void()> task) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            tasks_.push(std::move(task));
        }
        ready_.notify_one();
    }

    void wait_idle() {
        std::unique_lock<std::mutex> lock(mutex_);
        idle_.wait(lock, [this] { return tasks_.empty() && active_ == 0; });
    }

private:
    void worker_loop() {
        while (true) {
            std::function<void()> task;
            {
                std::unique_lock<std::mutex> lock(mutex_);
                ready_.wait(lock, [this] { return stopping_ || !tasks_.empty(); });
                if (stopping_ && tasks_.empty()) {
                    return;
                }
                task = std::move(tasks_.front());
                tasks_.pop();
                ++active_;
            }
            task();
            {
                std::lock_guard<std::mutex> lock(mutex_);
                --active_;
            }
            idle_.notify_all();
        }
    }

    std::vector<std::thread> workers_;
    std::queue<std::function<void()>> tasks_;
    std::mutex mutex_;
    std::condition_variable ready_;
    std::condition_variable idle_;
    std::size_t active_{0};
    bool stopping_{false};
};

int main() {
    constexpr int kTasks = 6;
    SimplePool pool(3);
    std::mutex output_mutex;

    for (int i = 1; i <= kTasks; ++i) {
        pool.post([i, &output_mutex] {
            const int square = i * i;
            std::lock_guard<std::mutex> lock(output_mutex);
            std::cout << "task " << i << " -> " << square << '\n';
        });
    }

    pool.wait_idle();
    std::cout << "processed=" << kTasks << '\n';
    return 0;
}
