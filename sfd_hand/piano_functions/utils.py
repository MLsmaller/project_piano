#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import os,random
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--video_Savepath", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/video2.avi",
                    help="要生成的视频路径")
parser.add_argument("--fps", type=int, default=20,
                    help="the fps of video")
parser.add_argument("--img_path", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/res_img",
                    help="图片的存储途径")                                        
args = parser.parse_args()

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

if __name__=="__main__":
    form_video(args.img_path, args.fps, args.video_Savepath)
