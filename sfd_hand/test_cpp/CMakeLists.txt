cmake_minimum_required(VERSION 2.8)
project(dif)
FIND_PACKAGE(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIR})
include_directories(${CMAKE_CURRENT_LIST_DIR}/functions/headers)
set(CMAKE_CXX_FLAGS "-std=c++0x")

file(GLOB SOURCE_FILES enhance_light.cpp ./functions/*.cpp)  #添加源文件,函数的cpp文件也记得添加进去
add_executable(dif ${SOURCE_FILES})
TARGET_LINK_LIBRARIES(dif ${OpenCV_LIBS})