#-*- coding:utf-8 -*- 
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import cv2
import os
import argparse
import time

from piano_utils.bwlabel import  key_loc
from piano_utils.keyboard import find_Rect
from piano_utils.utils import find_base, illumination
from piano_utils.data import near_white, form_img
from piano_utils.process_txt import form_onset
from demo import detect

parser = argparse.ArgumentParser()
parser.add_argument("--img_path", type=str, default='/home/data/cy/projects/piano/data/imgs',
                    help="需要检测的视频的路径")
parser.add_argument("--dif_savepath", type=str, default='/home/data/cy/projects/piano/data/dif_imgs',
                    help="差分图像的存储图像")
parser.add_argument("--w_txt_savepath", type=str, default='/home/data/cy/projects/piano/data/realtxt/video_realtxt_w',
                    help="白键真实标签按键的txt文件存储路径")
parser.add_argument('--thresh', default=0.7, type=float,
                    help='Final confidence threshold')
parser.add_argument('--gpu_ids', type=str, default="2,3",
                    help="gpu id ")                                               
parser.add_argument('--video_name', type=str, default="level_6_no_6",
                    help="需要检测的视频路径")
parser.add_argument('--keys_model', type=str, default="keys_900_torch0.3.pth",
                    help="选择按键的模型")
parser.add_argument('--hand_model', type=str, default="sfd_hand_lr_40000.pth",
                    help="选择检手的模型")                                  
args = parser.parse_args()

dir_list = [os.path.join(args.img_path, x) for x in os.listdir(args.img_path)] #---视频帧路径
model_root = '/home/data/cy/projects/piano/weights/'
keys_modelPath = '{}keys/{}'.format(model_root, args.keys_model)
hand_modelPath = '{}hand/{}'.format(model_root, args.hand_model)


if __name__ == "__main__":

    crop_path = '/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/final' #--裁剪后图像存储路径
    w_thres = 0.4  #---判断钢琴区域内某一行上白色像素累计总数值
    binary_thres = 180  #----对钢琴键盘二值化的阈值
    adjustNum = 0.038  #----是否调整每行的积累的阈值
    adj_light = 0.4  #----是否进行光照的调整
    
    
    for imgdir in dir_list:  #---遍历每个视频
        dif_path = '{}/{}'.format(args.dif_savepath, os.path.basename(imgdir))
        txt_path = '{}/{}_w.txt'.format(args.w_txt_savepath, os.path.basename(imgdir))
        # print(txt_path)
        # begin_num = 0  #---第一次检测到钢琴图像的下标索引  
        #---像数字\字母\元组为不可变对象,传入函数后传入的是值并不是地址,相同数字都指向同一个地址(地址共享的),函数外无效
        #---对于dict\list而言是可变对象,传入的是地址,创建可变对象会分配新地址
        if os.path.basename(imgdir) == 'level_8_no_2':
            print(imgdir)
            img_list = [os.path.join(imgdir, x) for x in os.listdir(imgdir)]
            img_list.sort()
            #----得到钢琴键盘的box
            Rect, begin_num = find_Rect(img_list, crop_path, w_thres, binary_thres, adjustNum, adj_light)
            print(Rect)
            print('第一次检测到钢琴图像的图片为{}'.format(begin_num))
            
            #----得到背景图的索引
            best_index = 0
            # best_index=find_base(img_list, begin_num, Rect) #---为了方便先注释掉
            # best_index = 1089   #----level_1_no_2的背景帧
            # best_index = 3643   #----level_1_no_1的背景帧
            # best_index = 968   #----level_1_no_3的背景帧
            # best_index = 678   #----level_1_no_6的背景帧
            # best_index = 1259   #----level_1_no_10的背景帧
            # best_index = 908  #----level_6_no_6的背景帧
            best_index = 816   #----level_8_no_2的背景帧
            print('最适合作为背景帧的图片索引为 {} '.format(best_index))
            w_base_img = cv2.imread(img_list[best_index])
            base_img = w_base_img[Rect[1]:Rect[3], Rect[0]:Rect[2]]
            
            #----得到白键和黑键的坐标
            white_loc = []  
            black_boxes = [] 
            total_top = []  
            total_bottom = [] 
            key_loc(base_img, white_loc, black_boxes, total_top, total_bottom)
            

            # pro_txt = '/home/data/cy/projects/piano/data/realtxt/detect_txt_w/level_8_no_2.txt'
            # pro_onset = '/home/data/cy/projects/piano/data/realtxt/detect_onsetxt_w/level_8_no_2_onset.txt'
            # if os.path.exists(pro_onset):
            #     os.remove(pro_onset)
            # form_onset1(pro_txt, pro_onset)
            
            # #---画出带编号的图片---
            # for path in img_list:
            #     img = cv2.imread(path)
            #     draw_img = img[Rect[1]:Rect[3], Rect[0]:Rect[2]]
            #     h, w = draw_img.shape[:2]
            #     num_savepath = '/home/data/cy/projects/piano/data/res/num_imgs'
            #     num_path = '{}/{}'.format(num_savepath, os.path.basename(imgdir))
            #     if not os.path.exists(num_path):
            #         os.mkdir(num_path)
            #     for j,loc in enumerate(white_loc):
            #         cv2.putText(draw_img, str(j + 1), (int( white_loc[j] + 2), int(0.8 * h)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 1)
            #         print(path)
            #         cv2.imwrite(os.path.join(num_path, os.path.basename(path)), draw_img)
            

            #----将当前图像与背景图进行差分dif--
            #----差分图像存储路径
            if not os.path.exists(dif_path):
                os.mkdir(dif_path)
            # for del_path in [os.path.join(dif_path, x) for x in os.listdir(dif_path)]:
            #     os.remove(del_path)
            base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
            stepsize = 0

            for index in range(begin_num, len(img_list)):
                t1 = time.time()
                path = img_list[index]
                print(path)
                w_cur_img = cv2.imread(path)
                cur_img = w_cur_img[Rect[1]:Rect[3], Rect[0]:Rect[2]]
                cur_img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
                #-----光照归一化------
                illumination(cur_img, base_img, stepsize)
                dif_img = cur_img - base_img
                differ = cv2.absdiff(base_img, cur_img)
                cv2.imwrite(os.path.join(dif_path, os.path.basename(path)), differ)
                t2 = time.time()
                print('{} has cost {:.2f} s'.format(path, t2 - t1))
                # print(os.path.join(dif_path, os.path.basename(path)))
                if index >= 0:
                    break
            dif_list = [os.path.join(dif_path, x) for x in os.listdir(dif_path)]
            dif_list.sort()

            
            del_path = '/home/data/cy/projects/piano/data/train/test_dir/' + os.path.basename(imgdir)
            if not os.path.exists(del_path):
                os.mkdir(del_path)
            del_list = [os.path.join(del_path, x) for x in os.listdir(del_path)]
            for del_img in del_list:
                os.remove(del_img)
            tostop = 0

            w_txt_path = '/home/data/cy/projects/piano/data/realtxt/detect_txt_w'
            cur_path = '{}.txt'.format(os.path.join(w_txt_path, os.path.basename(imgdir)))
            print('cur txt path is {}'.format(cur_path))
            if os.path.exists(cur_path):
                os.remove(cur_path)
            fout = open(cur_path, 'w')
            
            #-----当前检测的视频的路径,得到其fps,因为要知道时间----
            video_root = '/home/data/gx'
            video = '{}/{}.mp4'.format(video_root, os.path.basename(imgdir))
            cap = cv2.VideoCapture(video)
            if not cap.isOpened():
                print('error open video')
            fps = cap.get(cv2.CAP_PROP_FPS)
            rate = float(1.0 / fps)    #----1帧表示多少秒
            
            #-----开始逐帧检测白键是否被按下----
            for j, path in enumerate(img_list):
                if j < begin_num:
                    continue
                tostop += 1
                #------根据检手模型得到手的box---
                hand_box = detect(path, args.thresh, Rect,hand_modelPath)
                #----找到手所在的白键范围
                index_list = near_white(white_loc, hand_box)
                if index_list is not None:
                    #------逐个白键去检测是否被按下---
                    form_img(path, index_list, dif_list, white_loc, fout, rate, keys_modelPath)
                if tostop > 10:
                    break
            fout.close()



