#-*- coding:utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import cv2
import numpy
import argparse
import os
import shutil

data_path = '/home/data/cy/projects/piano/video'

audio_txt = os.path.join(data_path, 'video1_crop.txt')
w_txt=os.path.join(data_path,'w_key.txt')
b_txt=os.path.join(data_path,'b_key.txt')


parser = argparse.ArgumentParser(description=' count the accuary of pressed_keys projects')
parser.add_argument('--audio_txt', type=str, default=audio_txt,
                    help='the cnn of audio reslut')
parser.add_argument('--w_txt', type=str, default=w_txt,
                    help='save the cnn result to white key')
parser.add_argument('--b_txt', type=str, default=b_txt,
                    help='save the cnn result to black key')
parser.add_argument('--project_onset', type=str, default='/home/data/cy/projects/piano/project_onset1.txt',
                    help='算法跑出来的onset文件')
parser.add_argument('--audio_onset', type=str, default='/home/data/cy/projects/piano/audio/w_key.txt',
                    help='音频跑出来的onset文件')
parser.add_argument('--real_onset', type=str, default='/home/data/cy/projects/piano/real_onset1.txt',
                    help='自己标好的onset文件')
args = parser.parse_args()


black_num = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43,
            46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79,82, 84, 86]
white_num = []
for i in range(1, 89):
    if i not in black_num:
        white_num.append(i)
print(white_num)

#----将cnn检测到的txt分为白键和黑键两个txt，白键范围是1-52，黑键是1-36
def white_black_txt(audio_txt, w_txt, b_txt):
    #------将cnn检测到的按键编号减去21,变为从1开始-------
    offset = 20
    with open(audio_txt, 'r') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        temp_lines = []
        line = line.strip().split()
        for j, data in enumerate(line):
            if not (j == 2):
                temp_lines.append(data)
            else:
                temp_lines.append(str(int(data) - offset))
            
        new_lines.append(temp_lines)

    if os.path.exists(w_txt):
        os.remove(w_txt)
    if os.path.exists(b_txt):
        os.remove(b_txt)

    w_out = open(w_txt, 'w')
    b_out = open(b_txt, 'w')

    for line in new_lines:
        #line = line.strip().split()
        index = int(line[2])    #line[2]是一个字符串类型,需要转换为int,不然肯定不在list中
        if index in black_num:
            Bkey_index = black_num.index(index) + 1  #查看元素在list中的索引
            line[2] = str(Bkey_index)    
            for data in line:
                b_out.write('{} '.format(data))
            b_out.write('\n')
        else:
            Wkey_index = white_num.index(index) + 1 #找到原来txt中白键的编号在white_num中的位置,然后变为1-52按键范围(与标签数据对齐)
            line[2] = str(Wkey_index)
            for data in line:
                w_out.write('{} '.format(data))
            w_out.write('\n')
    b_out.close()
    w_out.close()
    print('the txt file has done')

#-------计算算法跑出的结果和真实结果进行比较-------
def count_acuuracy(project_onset, real_onset):
    with open(project_onset, 'r') as f:
        lines1 = f.readlines()
    audio_keys = []
    audio_times = []
    project_img = []
    audio_res = []
    for line in lines1:
        line = line.strip().split()
        audio_keys.append(int(line[2]))
        audio_times.append(float(line[1]))
        project_img.append(line[0])
        audio_res.append((float(line[1]), int(line[2])))
    audio_res = sorted(audio_res, key=lambda x: (x[0],x[1]))   #对List中元素先按照第一个排序再按照第二个排序
    #print(audio_res)

    with open(real_onset, 'r') as f:
        lines2 = f.readlines()
    real_keys = []
    real_times = []
    real_img = []
    real_res = []

    for line in lines2:
        line = line.strip().split()
        real_img.append(line[0])
        real_keys.append(line[2])
        real_times.append(line[1])
        real_res.append((float(line[1]), int(line[2])))
    real_res = sorted(real_res, key=lambda x: (x[0],x[1]))
    
    #print(real_res)
    offset = 0.1
    right_keys = []
    right_keys1 = []
    for i, w_key in enumerate(real_res):
        cur_time = w_key[0]
        cur_key = w_key[1]
        for audio_key in audio_res:
            if (abs(cur_time - audio_key[0]) < offset):
                if (cur_key == audio_key[1]):
                    right_keys.append(audio_key)  #时间是按照算法的时间来存取的
                    right_keys1.append(w_key)     #时间是按照自己标的时间来存取的
                #print(audio_key)
    right_keys = sorted(right_keys, key=lambda x: (x[0],x[1]))
    #print('the right keys is {}'.format(right_keys))


    #----这个是多检的按键-----
    over_keys = []
    over_filename = []
    for j,key in enumerate(audio_res):
        if key not in right_keys:
            over_keys.append(key)
            over_filename.append((project_img[j], key[1]))

    #---将多检的img移动到指定目录下
    #print(over_filename)
    save_path = '/home/data/cy/projects/piano/result'
    pressed_path = '/home/data/cy/projects/piano/result/error_img/pressed_white/'
    if not (os.path.exists(pressed_path)):
        os.mkdir(pressed_path)
    shutil.rmtree(pressed_path)   #os.path.dirname()得到文件的路径
    os.mkdir(pressed_path)   #shutil.rmtree()删除目录然后os.mkdir再创建目录
    for img_list in over_filename:
        base_name = os.path.basename(img_list[0])
        press_img_path = '{}/pressed_white/white_{}'.format(save_path, base_name)
        press_new_path = os.path.join(pressed_path, base_name)
        shutil.copy(press_img_path, press_new_path)


    #----这个是漏检的按键-----
    less_keys = []
    less_filename = []
    for j,key in enumerate(real_res):
        if key not in right_keys1:
            print(key) 
            less_keys.append(key)
            less_filename.append((real_img[j], key[1]))

    #print(less_filename)
    #---将漏检的img移动到指定目录下
    detect_path = '/home/data/cy/projects/piano/result/error_img/w_detect/'
    if not (os.path.exists(detect_path)):
        os.mkdir(detect_path)
    shutil.rmtree(detect_path)   
    os.mkdir(detect_path)  
    for img_list in less_filename:
        base_name = os.path.basename(img_list[0])
        diff_img_path = '{}/w_detect/pos_{}'.format(save_path, base_name)
        diff_new_path = os.path.join(detect_path,base_name)
        shutil.copy(diff_img_path, diff_new_path)

    print("算法跑出来的结果如下: ")
    print('总共按键有 {} 个'.format(len(real_res)))
    print('算法检测到的总按键有 {} 个'.format(len(audio_res)))
    print('算法检测到的正确按键有 {} 个, 多检有 {} 个, 漏检有 {} 个'.format(len(right_keys),len(over_filename),len(less_filename)))
    print('召回率为: {}'.format(len(right_keys) / len(real_res)))
    print('准确率: {}'.format(len(right_keys) / len(audio_res)))


#-------计算音频跑出的结果和真实结果进行比较-------
def count_acuuracy_audio(audio_onset, real_onset,to_stop):
    with open(audio_onset, 'r') as f:
        lines1 = f.readlines()
    audio_keys = []
    audio_times = []
    audio_res = []
    for j,line in enumerate(lines1):
        line = line.strip().split()
        audio_keys.append(int(line[2]))
        audio_times.append(float(line[0]))
        audio_res.append((float(line[0]), int(line[2])))
        if (j > to_stop):
            break
    audio_res = sorted(audio_res, key=lambda x: (x[0],x[1]))   #对List中元素先按照第一个排序再按照第二个排序
    #print(audio_res)

    with open(real_onset, 'r') as f:
        lines2 = f.readlines()
    real_keys = []
    real_times = []
    real_img = []
    real_res = []

    for line in lines2:
        line = line.strip().split()
        real_img.append(line[0])
        real_keys.append(line[2])
        real_times.append(line[1])
        real_res.append((float(line[1]), int(line[2])))
    real_res = sorted(real_res, key=lambda x: (x[0],x[1]))
    
    #print(real_res)
    offset = 0.1   #时间放的比较宽泛
    right_keys = []
    right_keys1 = []
    for i, w_key in enumerate(real_res):
        cur_time = w_key[0]
        cur_key = w_key[1]
        for audio_key in audio_res:
            if (abs(cur_time - audio_key[0]) < offset):
                if (cur_key == audio_key[1]):
                    right_keys.append(audio_key)  #时间是按照算法的时间来存取的
                    right_keys1.append(w_key)     #时间是按照自己标的时间来存取的
                #print(audio_key)
    right_keys = sorted(right_keys, key=lambda x: (x[0],x[1]))
    #print('the right keys is {}'.format(right_keys))


    #----这个是多检的按键-----
    over_keys = []
    for j,key in enumerate(audio_res):
        if key not in right_keys:
            over_keys.append(key)

    #----这个是漏检的按键-----
    less_keys = []
    less_filename = []
    for j,key in enumerate(real_res):
        if key not in right_keys1:
            less_keys.append(key)
            less_filename.append((real_img[j], key[1]))
    print("\n")
    print("音频跑出来的结果如下: ")
    print('总共按键有 {} 个'.format(len(real_res)))
    print('音频检测到的总按键有 {} 个'.format(len(audio_res)))
    print('音频检测到的正确按键有 {} 个, 多检有 {} 个, 漏检有 {} 个'.format(len(right_keys),len(over_keys),len(less_filename)))
    print('召回率为: {}'.format(len(right_keys) / len(real_res)))
    print('准确率: {}'.format(len(right_keys) / len(audio_res)))

if __name__ == '__main__':
    #print(len(white_num))
    ToStop = 77  #音频的对应到现在标的这里是这么多个音符
    count_acuuracy(args.project_onset, args.real_onset)
    count_acuuracy_audio(args.audio_onset, args.real_onset,ToStop)
    #white_black_txt(args.audio_txt, args.w_txt, args.b_txt)
    
    


