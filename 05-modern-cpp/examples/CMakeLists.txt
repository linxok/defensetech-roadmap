cmake_minimum_required(VERSION 3.16)
project(MavlinkParser VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(parser src/main.cpp src/mavlink_parser.cpp)

target_include_directories(parser PRIVATE include)

target_compile_options(parser PRIVATE -Wall -Wextra -Wpedantic)

enable_testing()
add_executable(test_parser tests/test_parser.cpp src/mavlink_parser.cpp)
add_test(NAME parser_test COMMAND test_parser)
