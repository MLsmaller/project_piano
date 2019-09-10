#-*- coding:utf-8 -*-

import cv2
import numpy as np
import os

#----想要得到包含钢琴的矩形框------
img = cv2.imread("/home/data/cy/projects/piano/KJnotes/frames1/whole_img/0000.jpg")
#img = cv2.imread("/home/data/cy/projects/piano/frame/video1_whole_frame/0100.jpg")
print(img.shape)
img_ori = img.copy()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
width = img.shape[1]  #img.shape  [height(rows),width(cols),channels]
print("the width is {}".format(width))

gray = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(gray, 50, 200, 3)
cv2.imwrite("./canny.jpg", edges)

lines = cv2.HoughLines(edges,1,np.pi/180,250)
lines1 = lines[:,0,:]#提取为二维
for rho, theta in lines1[:]:
    print(theta)
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a*rho
    y0 = b*rho
    x1 = int(x0 + 1000*(-b))
    y1 = int(y0 + 1000*(a))
    x2 = int(x0 - 1000*(-b))
    y2 = int(y0 - 1000*(a)) 
    cv2.line(img,(x1,y1),(x2,y2),(255,0,0),1)
cv2.imwrite("./test_hough.jpg", img)

#-------测试一下包含键盘的矩形框的坐标是多少--------
test_img=cv2.imread("/home/data/cy/projects/piano/KJnotes/frames2/whole_img/0608.jpg")
Rect = (32, 499, 1260 , 639 )
print(Rect[0])
crop_img = test_img[Rect[1]:Rect[3], Rect[0]:Rect[2]]
cv2.imwrite("./crop_img.jpg", crop_img)



""" maxLineGap = 0
minLineLength = 0.9*width
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 320, 0.9*width, maxLineGap)
print(lines)

if lines is not None:    
    lines1 = lines[:,0,:]#提取为二维
    for x1,y1,x2,y2 in lines1[:]: 
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

cv2.imwrite("./test_hough.jpg", img) """

