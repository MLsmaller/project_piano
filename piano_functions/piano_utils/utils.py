#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import os,random
import numpy as np
import json,math
import argparse
import struct, midi
import sys
from piano_utils.bwlabel import bwlabel,remove_region

black_num = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43,
            46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79,82, 84, 86]
white_num = []
for i in range(1, 89):
    if i not in black_num:
        white_num.append(i)
# print(white_num)

miditxt_Savepath = "/home/data/cy/projects/piano/KJnotes/midi/txt/"


#-----设置为函数之后这样别的函数调用时就不会影响别的parser参数,当导入别的函数时若其他函数也包含parser模块会导致混乱
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_Savepath", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/video2.avi",
                        help="要生成的视频路径")
    parser.add_argument("--fps", type=int, default=20,
                        help="the fps of video")
    parser.add_argument("--img_path", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/res_img",
                        help="图片的存储途径")
    parser.add_argument("--midi_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/02级_04_二月里来.mid",
                        help="需要解析的midi文件的路径")
    # parser.add_argument("--w_txt_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/txt/w_frame2.txt",
    #                     help="将midi文件中读取到的白键和时间信息存储为txt文件")                                                
    # parser.add_argument("--b_txt_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/txt/b_frame2.txt",
    #                     help="将midi文件中读取到的黑键和时间信息存储为txt文件")           
    parser.add_argument("--test_path", type=str, default="/home/data/cy/projects/piano/initial_video/frame/video1_whole_frame/0000.jpg",
                        help="用以测试的图片 ")
    parser.add_argument("--gamma", type=int, default=0.5,
                        help="光照补偿系数,越小就越亮")
    args = parser.parse_args()
    return args
    
#------计算钢琴下方1/3处的平均亮度(rgb图片)
def count_brightness(img):
    h, w, c = img.shape[:3]
    pixels = []
    for i in range(h):
        for j in range(w):
            for k in range(c):
                if i > (2.0 / 3) * h:
                    pixels.append(img[i, j, k])
    aver_pixel = sum(pixels) / len(pixels)
    return aver_pixel

#-----得到最适合用作背景的图片(从第一次检测到钢琴图片后开始遍历)--
def find_base(img_list, begin_num, Rect):
    base_img = cv2.imread(img_list[begin_num])   #---原始图片
    crop_img = base_img[Rect[1]:Rect[3], Rect[0]:Rect[2]]  #---crop后的图片
    ori_img = crop_img.copy()
    #----计算图片下2/3处的平均像素值大小
    brightness = count_brightness(ori_img)
    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    #----移除钢琴区域边界处的一些像素(可能不连续,用以检测连通区域黑键)
    crop_img = remove_region(crop_img)
    _, crop_img = cv2.threshold(crop_img, 130, 255, cv2.THRESH_BINARY) 
    crop_img = cv2.GaussianBlur(crop_img, (5, 5), 0)
    cv2.imwrite('./imgs/res/{}'.format(os.path.basename(img_list[begin_num])), crop_img)
    
    #----区域连通算法,检测黑键--
    feather = {}
    num = bwlabel(crop_img, ori_img, feather)
    
    test_num = 1070  #---为了加快速度
    
    for j in range(786, len(img_list)):
        whole_frame = cv2.imread(img_list[j])
        print(img_list[j])
        frame = whole_frame[Rect[1]:Rect[3], Rect[0]:Rect[2]]  #---crop img
        brightness1 = count_brightness(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = remove_region(frame)
        _, frame = cv2.threshold(frame, 150, 255, cv2.THRESH_BINARY) #----将阈值设大一点(本来是130),有利于检测黑键0.0,对于level_no_1视频
        frame = cv2.GaussianBlur(frame, (5, 5), 0)
        cv2.imwrite('/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/final/{}.jpg'.format(os.path.basename(img_list[j])[:-4]), frame)
        #----检测当前帧的黑键数量和亮度
        feather1 = {}
        num1 = bwlabel(frame, frame, feather1)
        print(num, brightness)
        print(num1, brightness1)
        if num == 36:
            if brightness1 > brightness and num1 == 36:
                brightness = brightness1
                best_index = j
        else:
            if brightness1 > brightness and num1 > num:
                brightness = brightness1
                num = num1
                best_index = j
        if num1 == 1 or num1 == 3:  #---视频后面的那些没用的帧
            break
    return best_index

#----进行光照归一化操作----
def illumination(src, overlay, stepsize):
    h, w = src.shape[:2]
    for i in range(h):
        for j in range(w):
            v = int(overlay[i, j]) - int(src[i, j])
            # print(v)
            if v > 0:
                src[i, j] += stepsize if stepsize < v else v
                # print(src[i, j])
                # break

            elif v < 0:
                v = -v
                src[i, j] -= stepsize if stepsize < v else v

#-----用以生成视频,可观察一下检测的效果-----
def form_video(img_path, fps,video_Savepath):
    img_list = os.listdir(img_path)
    img_list.sort(key=lambda x: int(x[:-4]))   #----对图片进行排序,是对os.listdir()得到的结果eg:0621.jpg
    img_list1 = [os.path.join(img_path, x) for x in img_list]
    picknumber = 1
    sample = random.sample(img_list1, picknumber)
    img_str = "".join(sample)
    img_one = cv2.imread(img_str)
    h, w, c = img_one.shape   #---shape: h,w,c
    img_size = (w, h)
    
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    if os.path.exists(video_Savepath):
        os.remove(video_Savepath)
    videoWriter = cv2.VideoWriter(video_Savepath, fourcc, fps, img_size)
    for path in img_list1:
        print(path)
        img = cv2.imread(path)
        videoWriter.write(img)
    videoWriter.release()
    print(w,h)
    print("the video {} has done ".format(video_Savepath))

if __name__ == "__main__":
    args = parser()
    #form_video(args.img_path, args.fps, args.video_Savepath)

    videoname = os.path.basename(args.midi_path)[:-4]  #---[:-4]从开始到倒数第四个之前的字符串
    w_txt_path = os.path.join(miditxt_Savepath, "{}_w.txt".format(videoname))
    b_txt_path = os.path.join(miditxt_Savepath, "{}_b.txt".format(videoname))
    print(w_txt_path, b_txt_path)
    parse_midi(args.midi_path, w_txt_path,b_txt_path)


    