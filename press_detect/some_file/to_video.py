#-*- coding:utf-8 -*-

import numpy as np
import os
import cv2,random
import argparse

parser=argparse.ArgumentParser(description="imgTovideo demo")
parser.add_argument("--save_path",type=str,default="./sfd_hand/test_model",
                      help="Directory for img")
parser.add_argument("--save_video",type=str,default="./new.avi",
                      help="video name")
parser.add_argument("--fps",type=int,default=20,
                      help="the fps of video")
args=parser.parse_args()

def selectFile(fileDir):
    pathDir=os.listdir(fileDir) 
    picknumber=1
    sample=random.sample(pathDir,picknumber)
    print(sample)
    print(type(sample))  
    return sample

def video_save(fps,vid_path,img_path,img_size):
    fourcc=cv2.VideoWriter_fourcc(*"MJPG")
    videoWriter=cv2.VideoWriter(vid_path,fourcc,fps,img_size)
    for path in img_path:
        print(path)
        img=cv2.imread(path)
        videoWriter.write(img)
    videoWriter.release()


#取出路径中的一张图片得到其w和h,用以VideoWriter()函数中的参数
img_list=selectFile(args.save_path)
img_str="".join(img_list)   #"sep".join(seq),返回一个以分隔符seq连接各个元素后生成的字符串
img_path=os.path.join(args.save_path,img_str)

img_test=cv2.imread(img_path)
img_w=img_test.shape[1]
img_h=img_test.shape[0]
size=(img_w,img_h)

if os.path.exists(args.save_video):
    os.remove(args.save_video)
args.fps=20
img_size=(img_w,img_h)

file_list=[os.path.join(args.save_path,y) 
            for y in os.listdir(args.save_path) if y.endswith(".jpg")]
#fourcc=cv2.VideoWriter_fourcc(*"MPEG")
video_save(args.fps,args.save_video,file_list,img_size)

