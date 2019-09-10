#-*- coding:utf-8 -*-
from __future__ import division     #这样进行除法时就会输出小数
from __future__ import print_function
from __future__ import unicode_literals   #from __future__ import 需要放在文件开头

import os
import json
import argparse
#-----json文件存储的是代码跑出来的按键,txt文件存储的是实际按键------
root = "/home/data/cy/projects/piano"


txt_path = os.path.join(root, "real_video1.txt")
if not (os.path.exists(txt_path)):
    print("the txt file is not exits")

parser = argparse.ArgumentParser(description=' count the accuary of pressed_keys projects')
parser.add_argument('--json_path', type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/pressed_w2.json",
                    help='the json file produce by projects ')
parser.add_argument('--txt_path', type=str, default="/home/data/cy/projects/piano/real_video1.txt",
                    help='the keys label by myself')
parser.add_argument('--new_txt_path', type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/video2.txt",
                    help='将算法跑出来json存为txt文件')
parser.add_argument('--pressed_txt', type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/onset2.txt",
                    help='将算法跑出来结果存为txt-onset文件')
parser.add_argument('--real_onset', type=str, default="/home/data/cy/projects/piano/real_onset1.txt",
                    help='将自己标的数据存为txt-onset文件')

args = parser.parse_args()


#----将代码跑出来的json文件转换为带有时间的txt文件----
#----这种情况是对于标了真实数据(已知每一帧的时间)
def read_json(json_path, txt_path, new_txt_path):
    #------读取代码跑出来的按键的json文件--------
    if not (os.path.exists(json_path)):
        print("the json file is not exits")
    if os.path.exists(new_txt_path):
        os.remove(new_txt_path)
    J_fileName=[]
    J_key=[]
    with open(json_path, 'r') as f:   #----首先要打开文件,然后再是json.load
        data = json.load(f)
        for i in range(len(data)):
            index = "{:0>4d}".format(i)  #宽度为4，不足的话左边补充0
            #index = str(i)  #Int转换为string类型
            imgData = data[index]
            J_fileName.append(imgData["img_name"])
            key_list = imgData["key"]    #生成的json文件中按pressed key有重复元素
            #o_list = list(set(key_list))   #set设置为集合形式(去掉了重复元素,但此时是乱序的),再转换为list形式
            #J_key.append(sorted(o_list,key=key_list.index))  #按照原list中的数据进行排序
            J_key.append(key_list)

    print("json文件检测的图片数量为: {}".format(len(J_key)))

    #------读取自己标好的实际的按键txt文件--------
    T_fileName=[]   #存取文件名
    T_key=[]        #存取按键
    Time = []       #存取时间
    f = open(txt_path)     
    while 1:
        line = f.readline()
        if not line:
            break
        line_list1 = line.split(' ')  #首先分割一次(空格换行符回车)
        #标数据时有时候后面加了空格啥的导致成为了list中的元素,需要去掉
        line_list=[x.strip() for x in line_list1 if (x.strip()!='')]
        #x.strip()把字符串开头和结尾中的空白符都删除了,只保留删除后还有其他字符的元素
        T_fileName.append(line_list[0])
        Time.append(line_list[1])
        t_key = []
        length=len(line_list)  
        for i in range(2, length):
            t_key.append(int(line_list[i]))   #存入list中被按下的键，并转为Int类型
        T_key.append(t_key)
    if len(T_key) != len(J_key):
        print("the numbers of test img is different from real img")

    #-----转换为新的txt文件--------
    fout = open(new_txt_path, 'w')
    for i in range(len(J_key)):
        fout.write("{} ".format(T_fileName[i]))
        fout.write("{} ".format(Time[i]))
        for j, key in enumerate(J_key[i]):
            fout.write("{} ".format(key))
        fout.write("\n")
    fout.close()
    print("the new txt file has done")

#------将代码跑出来的按键转换为检测onset的文件,就是只记录被按下的键和按键的起始时间,以便比较
def read_realData(new_txt_path, pressed_txt):
    with open(new_txt_path, 'r') as f:
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

    if os.path.exists(pressed_txt):
        os.remove(pressed_txt)
    fout = open(pressed_txt, 'w')
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

#------将自己标的按键转换为检测onset的文件-------
def Parse_realdata(txt_path, real_onset):
    with open(txt_path, 'r') as f:
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
        if (i > 414):    #--将真实标的数据转换为onset文件时,因为只标到0207.jpg个,而算法跑出来的不用这样弄
            break
    #print(len(filenames), len(times), len(keys))

    if os.path.exists(real_onset):
        os.remove(real_onset)
    fout = open(real_onset, 'w')
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
                if w_key in list(last_keys):
                    set2.remove(w_key)   #不能set1.remove(),这样的话set1就改变了,下次for in 循环不会进行

            if len(set2) > 0:
                set2 = sorted(set2)
                for pressed_key in set2:
                    fout.write('{} '.format(filenames[i]))
                    fout.write('{} '.format(times[i]))
                    fout.write('{} '.format(pressed_key))
                    fout.write('\n')

        #print(len(set1))


if __name__ == "__main__":
    read_json(args.json_path, args.txt_path,args.new_txt_path)
    read_realData(args.new_txt_path, args.pressed_txt)
    Parse_realdata(args.txt_path, args.real_onset)




''' R_num=0
for i in range(img_num):
    J_pressed = set(J_key[i])
    T_pressed = set(T_key[i])   #先转换为集合,然后在求交集(并集)
    if (list(J_pressed)[0] or (list(T_pressed))[0]):
        set_c = J_pressed & T_pressed  #对于集合求交集,再转换为list
        list_c = list(set_c)
        R_num += len(list_c)
        
accuracy=R_num/J_num
print("检测准确率为 {}".format(accuracy)) '''

    



