#-*- coding:utf-8 -*- 
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import cv2
import os
import argparse
import json
import operator

from PIL import Image
from models.keys_model import detect_keys

#-----找到box中的白键范围------
def near_white(white_loc, boxes):
    index_list = []
    if boxes[0] is not None:  #------如果当前帧没有检测到手
        for box in boxes:   #----遍历每一个手
            min_loc = box[0][0]
            max_loc = box[1][0]
            diffs1 = []
            diffs2 = []
            for w_loc in white_loc:
                diff1 = abs(min_loc - w_loc)
                diff2 = abs(max_loc - w_loc)
                diffs1.append(diff1)
                diffs2.append(diff2)
            left_index = diffs1.index(min(diffs1))-1    #----左边的白键编号
            right_index = diffs2.index(min(diffs2))+1   #----右边的白键编号
            index_list.append((left_index,right_index))
        # print(index_list)
        return index_list
    else:
        return None

#-----生成训练数据图片和按键的txt文件---
def form_img(img_name, index_list,dif_list, white_loc,fout,rate,model_name):
    dif_path = os.path.dirname(dif_list[0])  #---差分图存储路径
    #----裁剪后的图像的存储路径
    data_path = '/home/data/cy/projects/piano/data/train/test_dir'
    data_savepath = '{}/{}'.format(data_path, os.path.basename(os.path.basename(dif_path)))
    # print('data_savepath is {}'.format(data_savepath))
    if not os.path.exists(data_savepath):
        os.mkdir(data_savepath)
    

    #---取出当前的差分图
    img_path = os.path.join(dif_path, os.path.basename(img_name))
    print('当前差分图为:{}'.format(img_path))
    dif_img = cv2.imread(img_path)
    h, w = dif_img.shape[:2]
    offset = 3
    whole_list = []
    for hand_list in index_list:
        for index in range(hand_list[0]-1, hand_list[1]):
            whole_list.append(index)

    whole_list = list(set(whole_list))   #----去掉重复元素
    whole_list.sort()
    print(whole_list)

    
    num_class = {0: 'unpress', 1: 'press'}
    if len(whole_list) > 1:
        num = 0
        keys_list = []
        for index in whole_list:
            print('当前对应的白键为:{}'.format(index))
            crop_img = dif_img[0:h, int(white_loc[index] - offset):int(white_loc[index+1] + offset)]
            save_name = '{}/{}_{}.jpg'.format(data_savepath, os.path.basename(img_name)[:-4], num)
            print(save_name)
            cv2.imwrite(save_name, crop_img)
            num += 1
            #-----将numpy格式转换为PIL格式(opencv读取后是BGR,先转换为RGB)
            PIL_img = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
            press = detect_keys(PIL_img,model_name)
            if press == 1:
                print("当前帧{} 有白键{}被按下".format(img_name, index + 1))
                keys_list.append(index + 1)
        frame_num = int(os.path.basename(img_name)[:-4])
        cur_time = float(frame_num * rate)
        print(cur_time)
        if len(keys_list) > 0:
            keys_list.sort()
            fout.write('{} '.format(img_name))
            fout.write('{} '.format(cur_time))
            for key in keys_list:
                fout.write('{} '.format(key))
            fout.write('\n')


#----根据手的box得到手的范围内的按键---

if __name__ == '__main__':
    video_name = 'level_1_no_2'
    json_path = '/home/data/cy/projects/piano/keypoint_json' #----关键点的存储路径
    json_name = '{}/{}.json'.format(json_path, video_name)
    filenames = []
    left_points = []
    right_points = []
    white_loc = []
    find_boundary(white_loc,json_name, left_points, right_points, filenames)
