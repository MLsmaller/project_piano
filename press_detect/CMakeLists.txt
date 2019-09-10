cmake_minimum_required(VERSION 2.8)
project(code_test)

FIND_PACKAGE(OpenCV REQUIRED) #用cmake查找opencv包
include_directories(${OpenCV_INCLUDE_DIR})  #变量就要用${}
include_directories(${CMAKE_CURRENT_LIST_DIR}/functions/headers/)
#将函数的头文件包含进去
#set(CMAKE_CXX_STANDARD 11)  #用c++11标准库编译
set(CMAKE_CXX_FLAGS "-std=c++0x")
#set(SOURCE_FILES keys_detect.cpp ./functions/bwlabel.cpp ./functions/get_keyboard.cpp) 

file(GLOB SOURCE_FILES detect.cpp ./functions/*.cpp) #匹配functions路径下后缀为.cpp的文件
add_executable(code_test ${SOURCE_FILES})
#上面括号里面的两个参数分别是工程项目名和我们要编译的文件名的意思，中间需要有一个空格
TARGET_LINK_LIBRARIES(code_test ${OpenCV_LIBS} -ljson)
#链接到OpenCV库的环节，只需要更改前面第一个参数为工程项目名即可