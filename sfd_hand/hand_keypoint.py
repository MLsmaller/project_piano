#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import torch
import argparse
import torch.nn as nn
import torch.utils.data as data
import torch.backends.cudnn as cudnn
import torchvision.transforms as transforms

import shutil
import cv2
import time
import numpy as np
from PIL import Image

from data.config import cfg
from s3fd import build_s3fd
from torch.autograd import Variable
from utils.augmentations import to_chw_bgr
from utils.detect_hand1 import detect
from utils.detect_type import detect_hand
from utils.convert_loc import hand_right, hand_left
from utils.shift_img import find_change
from utils.to_json import to_json,saveJsonFile
from utils.keypoint_detect import keypoint_det,draw_point
from utils.with_shake import detect_frame

from piano_functions.process_video import crop_video,crop_img,process_img

parser = argparse.ArgumentParser(description='s3df demo')
parser.add_argument('--save_dir', type=str, default='/home/data/cy/projects/piano/KJnotes/frames2',
                    help='Directory for detect result')
parser.add_argument('--model', type=str,
                    default='/home/data/cy/projects/object_detect/sfd_hand/weights/weights1/sfd_hand_60000.pth', help='trained model')
parser.add_argument('--cuda', type=bool, default=True,
                    choices=[False, True], help='use gpu')
parser.add_argument('--hand_thresh', default=0.90, type=float,
                    help='Final confidence threshold')
parser.add_argument('--keypoint_thresh', default=0.1, type=float,
                    help='threshold to show the keypoint')
parser.add_argument('--img_dir', type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/whole_img",
                    help='Directory for img to detect')
parser.add_argument('--dataset', type=str, default='hand',
                    help='decide how many classes in the network input')
parser.add_argument('--video_path', type=str, default="/home/data/cy/projects/piano/video1/frame2.mp4",
                    help="the video path of object video")
parser.add_argument('--txt_path', type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/txt/video2.txt",
                    help="将视频的帧保存为一个带时间的txt文件")

parser.add_argument('--json_path', type=str, default="/home/data/cy/projects/piano/KJnotes/json_dir/hand_keypoint2.json",
                    help="将每一帧的关键点信息保存为json文件")
parser.add_argument('--cropSavepath', type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/crop_img",
                    help="只含钢琴图片的帧的保存路径")
args = parser.parse_args()


if not os.path.exists(args.save_dir):
    os.makedirs(args.save_dir)
  
if not os.path.exists(args.img_dir):
    os.makedirs(args.img_dir)

use_cuda = torch.cuda.is_available() and args.cuda
if use_cuda:
    torch.set_default_tensor_type('torch.cuda.FloatTensor')
else:
    torch.set_default_tensor_type('torch.FloatTensor')
RootPath=os.getcwd()

FrameTostop=1000

if __name__ == '__main__':
    if args.dataset == 'hand':
        net = build_s3fd('test', cfg.HAND.NUM_CLASSES)
    else:
        net = build_s3fd('test', cfg.NUM_CLASSES)
        
    net.load_state_dict(torch.load(args.model))
    net.eval()
    if use_cuda:
        net.cuda()
        cudnn.benckmark = True

    #---将视频分帧和进行裁剪----
    Todivide = False
    Tocrop = False
    if (Todivide):
        crop_video(args.video_path, args.img_dir, args.txt_path)

    file_list=[x for x in os.listdir(args.img_dir) if x.endswith('jpg')]
    file_list.sort(key=lambda x:int(x[:-4]))  #有时候得到的list里面图片不是顺序排列,x[:-4]表示以倒数第四位.为分割线,按照.左边的数字从小到大排序
    img_list = [os.path.join(args.img_dir, x) for x in file_list]
    
    Rect = (32, 499, 1260, 639)
    if (Tocrop):
        crop_img(args.cropSavepath, img_list, Rect)   #---图像裁剪---
    
    currentFrame = 0
    test_list = [os.path.join(args.img_dir, x)
                 for x in os.listdir(args.img_dir) if x.startswith(('0500','jpg'))]
    t = time.time()
    h_type = []  #返回值为一个list的时候,首先要创建一个list变量
    point_loc_l = []
    point_loc_r = []
    false_num_l = []
    false_num_r = []
    change_img_l = []
    change_img_r = []
    ori_point_l=[]
    ori_point_r=[]
    res = []
    
    num = 0
    for path in img_list:
        print(path)
        print('\n')
        img = cv2.imread(path)
        if img is None:
            print("error read image")
        width = img.shape[1]
        height = img.shape[0]
        img_savepath = "/home/data/cy/projects/piano/KJnotes/frames2/box_img"  #----保存图片的检测手的box的图片
        box_l, box_r, h_type = detect_hand(net, path, args.hand_thresh,
                              use_cuda,img_savepath)  # 检测到的左/右手框
        print(box_l, box_r, h_type)
        
        point_loc_l, false_num_l, change_img_l, ori_point_l = hand_left(box_l, false_num_l, change_img_l,
                                                                 point_loc_l, img, args.keypoint_thresh, path,
                                                                 args.save_dir, currentFrame,ori_point_l)
        point_loc_r, false_num_r, change_img_r, ori_point_r = hand_right(box_r, false_num_r, change_img_r,
                                                            point_loc_r, img, args.keypoint_thresh, path,
                                                            args.save_dir, currentFrame,ori_point_r)
        res = to_json(ori_point_l, ori_point_r, res, path)
        num += 1
        
    if os.path.exists(args.json_path):
        os.remove(args.json_path)
    saveJsonFile(res, args.json_path)