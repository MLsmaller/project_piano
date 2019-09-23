#-*- coding:utf-8 -*-
#----shift the hand to the center of img,which can be 
#----easily detect 
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import numpy as np
import math, os
from skimage import data, filters
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_path", type=str, default="/home/data/cy/projects/piano/KJnotes/1音协五级 听妈妈讲那过去的事情.mp4",
                    help="视频的存储路径")
parser.add_argument("--save_path", type=str, default="/home/data/cy/projects/piano/KJnotes/frames1/whole_img",
                    help="将视频分帧后的存储路径")
parser.add_argument("--txt_path", type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/video1.txt",
                    help="将分帧后的图片存储为一个带有时间的txt文件")
parser.add_argument("--crop_path", type=str, default="/home/data/cy/projects/piano/KJnotes/frames1/crop_img",
                    help="将图片裁剪后的(只带有钢琴)所要存储的路径")
# parser.add_argument("--Rect",type=Rect,)                                        
args = parser.parse_args()

Rect = (41, 500, 1245, 634)   #--- (x,y,x+w,y+h)

if not os.path.exists(args.save_path):
    os.mkdir(args.save_path)
if not os.path.exists(args.crop_path):
    os.mkdir(args.crop_path)

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

#----将图片裁剪,用于其他文件调用函数时-----
def crop_img(crop_path, img_list, Rect):
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)
    
    for img1 in img_list:
        print(img1)
        imgTocrop = cv2.imread(img1)
        crop_img = imgTocrop[Rect[1]:Rect[3], Rect[0]:Rect[2]]
        cv2.imwrite(os.path.join(crop_path, os.path.basename(img1)), crop_img)

#----将图片裁剪,用于当前文件函数的调用-----
def crop_img1(crop_path, save_path, Rect):
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)
    file_list = [x for x in os.listdir(save_path)]
    file_list.sort(key=lambda x: int(x[:-4]))
    img_list = [os.path.join(save_path, x) for x in file_list
                if x.endswith(".jpg")]
    
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

def thrs_otsu(img):
    # gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res_img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    cv2.imwrite("./test_ostu.jpg", res_img)

#-------下面的可用于测试上面写的函数-----
if __name__ == "__main__":
    crop_video(args.video_path, args.save_path, args.txt_path)
    # crop_img1(args.crop_path, args.save_path, Rect)
    
    print(type(Rect))

    