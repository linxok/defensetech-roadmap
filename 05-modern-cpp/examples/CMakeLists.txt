cmake_minimum_required(VERSION 3.16)
project(ModernCppExamples VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(Threads REQUIRED)

add_executable(thread_pool thread_pool.cpp)
target_link_libraries(thread_pool PRIVATE Threads::Threads)
target_compile_options(thread_pool PRIVATE -Wall -Wextra -Werror)
