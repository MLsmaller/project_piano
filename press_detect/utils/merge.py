#-*- coding:utf-8 -*-
from __future__ import division     #这样进行除法时就会输出小数
from __future__ import print_function
from __future__ import unicode_literals   #from __future__ import 需要放在文件开头

import os
import json
import argparse
#-----json文件存储的是代码跑出来的按键,txt文件存储的是实际按键------
root = "/home/data/cy/projects/piano"
project_onset = os.path.join(root, 'project_onset1.txt')
real_onset = os.path.join(root, 'real_onset1.txt')
audio_onset = os.path.join(root, 'audio/w_key.txt')

project_new = os.path.join(root, 'detect/project_new.txt')
real_new = os.path.join(root, 'detect/real_new.txt')
audio_new = os.path.join(root, 'detect/audio_new.txt')

black_num = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43,
            46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79,82, 84, 86]
white_num = []
for i in range(1, 89):
    if i not in black_num:
        white_num.append(i)
print(white_num)
w_ori_num = []
for i in range(1, 53):
    w_ori_num.append(i)
print(w_ori_num)

#-----白键要变为原来的那种编号才可以-----
#-----将检测和标的txt文件转换为学姐可以对比的形式------ 
def delete_path(txt_path, new_path):
    with open(txt_path, 'r') as f:
        lines = f.readlines()

    if os.path.exists(new_path):
        os.remove(new_path)
    fout = open(new_path, 'w')

    for i, line in enumerate(lines):
        line = line.strip().split()
        for j in range(1, len(line)):
            if (j == 2):
                fout.write('{} '.format(float(line[1]) + 0.3))
                Index = int(line[j])
                w_Index = w_ori_num.index(Index)
                line[j] = white_num[w_Index]
                fout.write('{}'.format(line[j]))
            else:
                fout.write('{} '.format(line[j]))
        fout.write('\n')
    print('the {} file has done'.format(new_path))

#-----将学姐检测得到的txt文件转换为学姐可以对比的形式------
def delete_audio(txt_path, new_path):
    with open(txt_path, 'r') as f:
        lines = f.readlines()
    if os.path.exists(new_path):
        os.remove(new_path)     
    fout = open(new_path, 'w')

    for i, line in enumerate(lines):
        line = line.strip().split()
        line[1]=float(line[0])+0.3
        for j in range(len(line)):
            if (j == 2):
                Index = int(line[j])
                w_Index = w_ori_num.index(Index)
                line[j] = white_num[w_Index]
                fout.write('{}'.format(line[j]))
            else:
                fout.write('{} '.format(line[j]))
        fout.write('\n')
    print('the {} txt file has done'.format(new_path))


if __name__ == '__main__':
    delete_path(project_onset, project_new)
    delete_path(real_onset, real_new)
    delete_audio(audio_onset, audio_new)
