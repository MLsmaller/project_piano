cmake_minimum_required(VERSION 2.8)
project(keyboard)
FIND_PACKAGE(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIR})  #包含opencv库
set(CMAKE_CXX_STANDADR 11)

file(GLOB SOURCE_FILES keyboard.cpp)  #用GLOB包含可执行文件
add_executable(keyboard ${SOURCE_FILES})  #给工程添加可执行文件，存在变量SOURCE_FILES
TARGET_LINK_LIBRARIES(keyboard ${OpenCV_LIBS})  #链接到OpenCV库
