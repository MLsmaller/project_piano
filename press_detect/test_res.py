#-*- coding:utf-8 -*-
from __future__ import division     #这样进行除法时就会输出小数
from __future__ import print_function
from __future__ import unicode_literals   #from __future__ import 需要放在文件开头

import os
import json

#-----json文件存储的是代码跑出来的按键,txt文件存储的是实际按键------
root = os.getcwd()
json_path = os.path.join(root, "res/pressed_w.json")
if not (os.path.exists(json_path)):
    print("the json file is not exis")

txt_path = os.path.join(root, "res/new_data.txt")
if not (os.path.exists(txt_path)):
    print("the txt file is not exis")

J_fileName=[]
J_key=[]
with open(json_path, 'r') as f:
    data = json.load(f)
    for i in range(len(data)):
        index = "{:0>4d}".format(i)  #宽度为4，不足的话左边补充0
        #index = str(i)  #Int转换为string类型
        imgData = data[index]
        J_fileName.append(imgData["img_name"])
        key_list = imgData["key"]    #生成的json文件中按pressed key有重复元素
        o_list = list(set(key_list))   #set设置为集合形式(去掉了重复元素,但此时是乱序的),再转换为list形式
        J_key.append(sorted(o_list,key=key_list.index))  #按照原list中的数据进行排序

T_fileName=[]
T_key=[]   
f = open(txt_path)     #这里不和上面一样with open,with open之后只执行一次里面内容,而这里要逐行读取
while 1:
    line = f.readline()
    if not line:
        break
    line_list1 = line.split(' ')  #首先分割一次(空格换行符回车)
    #标数据时有时候后面加了空格啥的导致成为了list中的元素,需要去掉
    line_list=[x.strip() for x in line_list1 if (x.strip()!='')]
    #x.strip()把字符串开头和结尾中的空白符都删除了,只保留删除后还有其他字符的元素
    T_fileName.append(line_list[0])
    t_key = []
    length=len(line_list)  
    for i in range(1, length):
        t_key.append(int(line_list[i]))   #存入list中被按下的键，并转为Int类型
    T_key.append(t_key)
    
img_num = len(T_key)
if img_num != len(J_key):
    print("the numbers of test img is different from real img")

#----Json文件和txt文件检测到的总按键---
J_num=0
for i,list1 in enumerate(J_key):    #enumerate()返回元素下标索引和元素
    if not (list1[0] == 0):
        J_num += len(list1)
print("Json文件检测到的按键为 {}".format(J_num))

T_num=0
for i,list1 in enumerate(T_key):    #enumerate()返回元素下标索引和元素
    if not (list1[0] == 0):
        T_num += len(list1)
print("txt文件中的按键为 {}".format(T_num))

R_num=0
for i in range(img_num):
    J_pressed = set(J_key[i])
    T_pressed = set(T_key[i])   #先转换为集合,然后在求交集(并集)
    if (list(J_pressed)[0] or (list(T_pressed))[0]):
        set_c = J_pressed & T_pressed  #对于集合求交集,再转换为list
        list_c = list(set_c)
        R_num += len(list_c)
        
accuracy=R_num/J_num
print("检测准确率为 {}".format(accuracy))

    



