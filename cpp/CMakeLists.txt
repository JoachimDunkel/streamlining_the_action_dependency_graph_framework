cmake_minimum_required(VERSION 3.11)
project(dependency_creator)

find_package(Python3 REQUIRED COMPONENTS Development)
include_directories(${Python3_INCLUDE_DIRS})


include(FetchContent)

# Add the pybind11 library
FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.13.6
)
FetchContent_MakeAvailable(pybind11)
pybind11_add_module(dependency_creator src/dependency_creator.cpp)

# Add google-test
FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.1
)
FetchContent_MakeAvailable(googletest)
enable_testing()
add_executable(test_dependency_creator tests/test_dependency_creator.cpp)
target_link_libraries(test_dependency_creator gtest gtest_main gmock ${Python3_LIBRARIES} pybind11::module)
add_test(NAME test_dependency_creator COMMAND test_dependency_creator)
