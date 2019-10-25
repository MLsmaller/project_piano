#-*- coding:utf-8 -*- 
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import cv2
import os

#----移除钢琴边界处的一些像素----
def remove_region(img):
    if len(img.shape) == 3:
        print("please input a gray image")
    h, w = img.shape[:2]

    for i in range(h):
        for j in range(w):
            if (i < 0.05 * h or i > (2.0/3) * h):
                img[i, j] = 255
    
    for i in range(h):
        for j in range(w):
            if (j < 0.005 * w or j > 0.994 * w):
                img[i, j] = 255

    return img

#-----找到离白键最近的那个黑键--
def near_white(white_loc, black_boxes):
    diffs = []
    for i in range(len(black_boxes)):
        diff = abs(black_boxes[i][0] - white_loc)
        diffs.append(diff)
    index = diffs.index(min(diffs))
    return index
    

#---区域连通算法,检测黑键的位置--
def bwlabel(src, ori_img, feather):
    img_draw = ori_img.copy()
    #---可能threshold的时候对某些地方二值化会有一些小点,最后得到的box将其area中较小的排除即可
    h, w = src.shape[:2]
    area = 0

    rightBoundary = 0
    topBoundary = 0
    bottomBoundary = 0
    labelValue = 0
    feather.clear()
    
    dst = src.copy()  #--对于numpy数组.copy是完全复制,两个独立,对于listdst=src[:]是完全复制独立
    class Stack(object):
        #----list方式实现栈
        def __init__(self):
            self.items = []

        def is_empty(self):
            return self.items == []
        def peek(self):
            return self.items[len(self.items) - 1]
        def size(self):
            return len(self.items)
        def push(self, item):
            self.items.append(item)
        def pop(self):
            return self.items.pop()

    pointstack = Stack()

    feather['value'] = {}
    feather['value']['area'] = []
    feather['value']['boundinbox'] = []
    
    for i in range(h):
        for j in range(w):
            if dst[i, j] == 0:   #---这里应该表示的是第i行的j个元素,python中src为array,src[i,j]就是第i行第j列的元素
                area = 0
                labelValue += 1
                seed = (i, j)  #---这是
            #    print("the seed is {}".format(seed))
            #    print("dst[seed] is {}".format(dst[seed]))
                
                dst[seed] = labelValue
                pointstack.push(seed)
                # print(seed)
                area += 1
                leftBoundary = seed[1]
                rightBoundary = seed[1]
                topBoundary = seed[0]
                bottomBoundary = seed[0]   #---这个和C++版本的有区别

                while (not (pointstack.is_empty())):
                    neighbor = (seed[0], seed[1] + 1)  #---right
                    
                    if (seed[1] != (w - 1)) and (dst[neighbor] == 0):
                        dst[neighbor] = labelValue
                        pointstack.push(neighbor)
                        area += 1
                    if (rightBoundary < neighbor[1]):
                        rightBoundary = neighbor[1]

                    neighbor = (seed[0]+1, seed[1])  #---bottom
                    if ((seed[0] != (h - 1)) and (dst[neighbor] == 0)):
                        dst[neighbor] = labelValue
                        pointstack.push(neighbor)
                        area += 1
                        if (bottomBoundary < neighbor[0]):
                            bottomBoundary = neighbor[0]                    

                    neighbor = (seed[0], seed[1]-1)  #---left
                    if ((seed[1] != 0) and (dst[neighbor] == 0)):
                        dst[neighbor] = labelValue
                        pointstack.push(neighbor)
                        area += 1
                        if (leftBoundary > neighbor[1]):
                            leftBoundary = neighbor[1]   

                    neighbor = (seed[0]-1, seed[1])   #---top
                    if ((seed[0] != 0) and (dst[neighbor] == 0)):
                        dst[neighbor] = labelValue
                        pointstack.push(neighbor)
                        area += 1
                        if (topBoundary > neighbor[0]):
                            topBoundary = neighbor[0]                       
                    
                    seed = pointstack.peek()  #--取栈顶元素并出栈
                    pointstack.pop()
                    
                box = (leftBoundary, topBoundary, rightBoundary - leftBoundary, bottomBoundary - topBoundary)  #--(x,y,w,h)
                # cv2.rectangle(img_draw, (leftBoundary, topBoundary), (rightBoundary, bottomBoundary), (0, 0, 255), 2)
                
                if area>500:    #---排除一些小框框,二值化的时候表现的不太好
                    feather['value']['area'].append(area)
                    feather['value']['boundinbox'].append(box)
                    # print("loc is {}".format((box[0],box[1])))  
                    cv2.rectangle(img_draw, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 0, 255), 2)
    box_num = len(feather['value']['boundinbox'])  #---黑键的数量
    cv2.imwrite("./black_box.jpg", img_draw)
    return box_num

#----得到钢琴区域黑键和白键的位置,以及对应的box
def key_loc(base_img,white_loc,black_boxes,total_top,total_bottom):
    ori_img = base_img.copy()
    ori_img1 = base_img.copy()
    height, width = base_img.shape[:2]
    base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    #----移除钢琴区域边界处的一些像素(可能不连续,用以检测连通区域黑键)
    base_img = remove_region(base_img)
    #----level_1_no_1为150,level_1_no_2为130
    # _, base_img = cv2.threshold(base_img, 130, 255, cv2.THRESH_BINARY)    
    _, base_img = cv2.threshold(base_img, 150, 255, cv2.THRESH_BINARY) 
    base_img = cv2.GaussianBlur(base_img, (5, 5), 0)

    feather = {}
    #----区域连通算法,检测黑键--
    bwlabel(base_img, ori_img,feather)
    black_loc = []
    for box in feather['value']['boundinbox']:  #---字典类型,同时取k,v就是for k,v in dict.items(),取k是dict.keys(),v是dict.values()
        black_boxes.append(box)
        black_loc.append(box[0])  #---box左上角的横坐标

    #----得到白键的区域
    black_gap1 = black_loc[3] - black_loc[2]  #--第一个周期区域内的黑键间隔
    ratio = 23.0 / 41
    # ratio = 23.0 / 40
    whitekey_width1 = ratio * black_gap1  
    half_width1 = black_boxes[4][2]    #T1中第四个黑键被均分,从该位置开始算区域起始位置
    keybegin = black_loc[4] + half_width1 / 2.0-7.0 * whitekey_width1
    
    for i in range(10):
        if int(keybegin + i * whitekey_width1) < 0:
            cv2.line(ori_img, (2, 0), (2, height), (0, 0, 255), 1)
            white_loc.append(1)
        else:
            cv2.line(ori_img, (int(keybegin + i * whitekey_width1), 0), (int(keybegin + i * whitekey_width1), height), (0, 0, 255), 1)
            white_loc.append(keybegin + i * whitekey_width1)
    for i in range(6):  #----剩下的6个循环区域
        #----定义好每个区域的起始位置
        axis = 8 + i * 5
        black_gap2 = black_loc[axis] - black_loc[axis - 1]
        whitekey_width2 = ratio * black_gap2 
        half_width2 = black_boxes[axis + 1][2] 
        keybegin1 = black_loc[axis + 1] + float(half_width2 / 2.0) - 5.0 * whitekey_width2
        for j in range(1,8):
            cv2.line(ori_img, (int(keybegin1 + j * whitekey_width2), 0), (int(keybegin1 + j * whitekey_width2), height), (0, 0, 255), 1)
            white_loc.append(keybegin1 + j * whitekey_width2)
        if i == 5:  #----最后一次循环将钢琴最后一个白键加上
            if width < int(keybegin1 + 8 * whitekey_width2):
                white_loc.append(width - 1)
            else:
                white_loc.append(keybegin1 + 8 * whitekey_width2)
            cv2.line(ori_img, (int(white_loc[-1]), 0), (int(white_loc[-1]), height), (0, 0, 255))
        
    print("the number of whtiekey_num is {}".format(len(white_loc)))
    cv2.imwrite("./white_loc.jpg", ori_img)

    #--------找到白键所在的box---
    for i in range(1, len(white_loc)):
        white_x = white_loc[i - 1]
        white_width = white_loc[i] - white_x
        # print(white_x,white_width)
        if i == 1:
            top_box = (white_x, 0, black_boxes[i - 1][0] - white_x, 1.1 * black_boxes[i - 1][3]) #---(x,y,w,h)
            bottom_box=(white_x,1.1*black_boxes[i-1][3],white_width,height-1.1*black_boxes[i-1][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)

        elif i==2: 
            top_box = (black_boxes[i - 2][0]+black_boxes[i - 2][2], 0, white_loc[i] - (black_boxes[i - 2][0]+black_boxes[i - 2][2]), 1.1 * black_boxes[i - 2][3])
            bottom_box=(white_x,1.1*black_boxes[i-2][3],white_width,height-1.1*black_boxes[i-2][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)        

        elif (i == 3 or ((i - 3) % 7 == 0) and i < 52) or (i == 6 or ((i - 6) % 7 == 0) and i < 52):
            index = near_white(white_x, black_boxes)
            top_box = (white_x + 1, 0, black_boxes[index][0] - white_x - 1, 1.1 * black_boxes[index][3])
            bottom_box=(white_x,1.1*black_boxes[index][3],white_width+2,height-1.1*black_boxes[index][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)
            # print(top_box)
            # print(bottom_box)
        elif (i == 4 or ((i - 4) % 7 == 0) and i < 52) or (i == 7 or ((i - 7) % 7 == 0) and i < 52) or (i == 8 or ((i - 8) % 7 == 0) and i < 52):
            index = near_white(white_x, black_boxes)
            top_box = (black_boxes[index][0]+black_boxes[index][2], 0, black_boxes[index+1][0] - (black_boxes[index][0]+black_boxes[index][2]) - 1, 1.1 * black_boxes[index][3])
            bottom_box=(white_x,1.1*black_boxes[index][3],white_width+2,height-1.1*black_boxes[index][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)
        elif (i == 5 or ((i - 5) % 7 == 0) and i < 52) or (i == 9 or ((i - 9) % 7 == 0) and i < 52) or (i == 8 or ((i - 8) % 7 == 0) and i < 52):
            index = near_white(white_x, black_boxes)
            top_box = (black_boxes[index][0]+black_boxes[index][2], 0, white_loc[i] - (black_boxes[index][0]+black_boxes[index][2]) - 1, 1.1 * black_boxes[index][3])
            bottom_box=(white_x,1.1*black_boxes[index][3],white_width+2,height-1.1*black_boxes[index][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)
        #----最后一个框
        else:
            top_box = (white_x + 1, 0, white_loc[i] - white_x - 1, 1.1 * black_boxes[35][3])
            bottom_box = (white_x + 1, 1.1 * black_boxes[35][3], white_loc[i] - white_x - 1, height - 1.1 * black_boxes[35][3])
            total_top.append(top_box)
            total_bottom.append(bottom_box)            
        
    for box in total_top:
        cv2.rectangle(ori_img1, (int(box[0]), int(box[1])), (int(box[0]) + int(box[2]), int(box[1]) + int(box[3])), (0, 0, 255), 2)
    for i, box in enumerate(total_bottom):
        
        cv2.rectangle(ori_img1, (int(box[0]), int(box[1])), (int(box[0]) + int(box[2]), int(box[1]) + int(box[3])), (0, 0, 255), 2)
        cv2.putText(ori_img1, str(i + 1), (int(box[0] + 5), height), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 0), 1)
    cv2.imwrite('./darw_img.jpg', ori_img1)

if __name__ == "__main__":
    base_path = "/home/data/cy/projects/piano/KJnotes/frames7/crop_img/0828.jpg"  #---frames2
    base_img = cv2.imread(base_path)
    white_loc = []  #---存储白键的横坐标
    black_boxes = []  #---存储黑键的box
    total_top = []  #---存储白键区域上面的box
    total_bottom = [] #---存储白键区域下面的box
    key_loc(base_img, white_loc, black_boxes, total_top, total_bottom)
    
    



        
        
    
                
                
                


    