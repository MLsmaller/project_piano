#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import os
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser(description=" parse the pressed keys")
parser.add_argument("--json_path", type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/pressed_w2.json",
                    help="the json file path")
parser.add_argument("--ori_txtPath", type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/video2.txt",
                    help="the initial Img txt file(with time without keys) ")      
parser.add_argument("--new_txt", type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/pro_video2.txt",
                    help="the txtres by projects (with time and keys)")
parser.add_argument("--pro_onset", type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/pro_onset2.txt",
                    help="将算法跑出来的结果转换为onset的txt文件")
args = parser.parse_args()


#-----将算法跑出来的json文件转换为带时间和按键的txt文件(以便观察和比较)
def parse_json(json_path, txt_path,new_txt):

    J_fileName=[]
    J_key = []
    #----读取Json文件----
    with open(json_path, 'r') as f: 
        data = json.load(f)
        for i in range(len(data)):
            index = "{:0>4d}".format(i)  
            imgData = data[index]
            J_fileName.append(imgData["img_name"])
            key_list = imgData["key"]    
            J_key.append(key_list)

    print("json文件检测的图片数量为: {}".format(len(J_key)))

    #------读取图片的txt文件(有时间没有真实按键)--------
    T_fileName=[]   #存取文件名
    Time = []       #存取时间
    f = open(txt_path)     
    while 1:
        line = f.readline()   #---逐行读取,f.readlines()是一次性全部读
        if not line:
            break
        line_list1 = line.split(' ') 
        line_list=[x.strip() for x in line_list1 if (x.strip()!='')]
        T_fileName.append(line_list[0])
        Time.append(line_list[1])

    if len(Time) != len(J_key):
        print("the numbers of test img is different from real img")

    #-----转换为新的txt文件（即算法跑出来的带按键时间的txt文件）--------
    if os.path.exists(new_txt):
        os.remove(new_txt)
    fout = open(new_txt, 'w')
    for i in range(len(J_key)):
        fout.write("{} ".format(T_fileName[i]))
        fout.write("{} ".format(Time[i]))
        for j, key in enumerate(J_key[i]):
            fout.write("{} ".format(key))
        fout.write("\n")
    fout.close()
    print("the new txt file has done")

#-----将算法跑出来的结果转换为带onset的txt文件----
def form_onset(new_txt, pro_onset):

    with open(new_txt, 'r') as f:
        lines = f.readlines()
    filenames = []
    times = []
    keys = []
    
    for i, line in enumerate(lines):
        key = []
        line = line.strip().split()
        filenames.append(line[0])
        times.append(float(line[1]))
        for j in range(2, len(line)):
            key.append(int(line[j]))
        keys.append(key)
        #if (i > 208):    #--将真实标的数据转换为onset文件时,因为只标了207个,而算法跑出来的不用这样弄
            #break
    #print(len(filenames), len(times), len(keys))

    if os.path.exists(pro_onset):
        os.remove(pro_onset)
    fout = open(pro_onset, 'w')
    #pressed_keys = []
    #----对于两个list看他们的相同/不同元素可以转换为集合来求交并集-----
    for i in range(1,len(filenames)):
        current_keys = set(keys[i])
        last_keys = set(keys[i - 1])
        set1 = list(current_keys.symmetric_difference(last_keys))
        set2 = set1[:]  #python如何直接set2=set1这样复制的话改变其中一个两个都会变,因为其指向的都是一样的
                        #使用new=old[:]的话会创建新的列表,不会影响原来的
        if (0 in set2):
            set2.remove(0)

        if (len(set1) > 0):
            if 0 in set1:
                set1.remove(0)
            for w_key in set1:
                if w_key in list(last_keys):   #要的是当前帧与上一帧不同的按键,如果不同的按键在上一帧中说明此按键在上一帧中结束了,不要
                    set2.remove(w_key)   #不能set1.remove(),这样的话set1就改变了,下次for in 循环不会进行

            set3 = set2[:]
            #----如果当前帧得到的按键在前面5帧中都没有出现,则认为是新按下的,因为检测可能有些帧没检测出来
            if len(set2) > 0:
                for key in set2:
                    if (i - 5) > 0:
                        for m in range(1,6):
                            if key in keys[i - m]:
                                set3.remove(key)
                                break       #只要移除一次就够了,因为后面被移除之后就没有了
                    else:
                        for m in range(i):   #---对于视频的前5帧,只需要判断前面几帧是否有重复
                            if key in keys[m]:
                                set3.remove(key)
                                break
                set3 = sorted(set3)
                for pressed_key in set3:
                    fout.write('{} '.format(filenames[i]))
                    fout.write('{} '.format(times[i]))
                    fout.write('{} '.format(pressed_key))
                    fout.write('\n')

        #print(len(set1))


if __name__ == "__main__":
    parse_json(args.json_path, args.ori_txtPath, args.new_txt)
    form_onset(args.new_txt, args.pro_onset)