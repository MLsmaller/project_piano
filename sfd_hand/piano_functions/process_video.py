#-*- coding:utf-8 -*-
#----shift the hand to the center of img,which can be 
#----easily detect 
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import numpy as np
import math,os

#-----将视频分帧,生成一个带时间的txt文件----
def crop_video(video_path,save_path,txt_path):
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        print("the video is correct open")
    else:
        print("error open video")
    #--对于下面调用cap.get()函数需要对CAP_PROP_FRAME前面加上cv2.
    totalframe = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    rate = float(1.0 / fps)
    print(fps)

    flag = True
    frames = 0
    if os.path.exists(txt_path):
        os.remove(txt_path)
    fout = open(txt_path, 'w')
    
    while (flag):
        flag, frame = cap.read()
        if (flag == False):   #最后一帧图片时,变为False，此帧图片就不用进行存储了
            break
        img_name = "{}/{:0>4d}.jpg".format(save_path, frames)
        cv2.imwrite(img_name, frame)
        
        cur_time = (frames + 1) * rate
        fout.write("{} {}".format(img_name, cur_time))
        fout.write("\n")
        print("cur_time is {}".format(cur_time))
        frames += 1
    fout.close()
    print("the txt file {} has done ".format(txt_path))
        #print(img_name)

#----将图片裁剪-----
def crop_img(crop_path, img_list, Rect):
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)
    for img1 in img_list:
        print(img1)
        imgTocrop = cv2.imread(img1)
        crop_img = imgTocrop[Rect[1]:Rect[3], Rect[0]:Rect[2]]
        cv2.imwrite(os.path.join(crop_path, os.path.basename(img1)), crop_img)

#----将图片上方的像素进行处理一下---
def process_img(img, Rect):
    h, w, c = img.shape
    for row in range(h):   #---遍历每一行
        for col in range(w):  #---遍历每一列
            for channel in range(c):
                if (row < Rect[1]-15):
                    #print(img_path)
                    img[row][col][channel]=128
    return img
        
#-------下面的可用于测试上面写的函数-----
if __name__ == "__main__":
    video_path = "/home/data/cy/projects/piano/KJnotes/frame2.mp4"
    save_path = "/home/data/cy/projects/piano/KJnotes/frames2/whole_img"  #---随便写的
    txt_path = "/home/data/cy/projects/piano/KJnotes/json_dir/txt/video2.txt"
    crop_video(video_path,save_path,txt_path)