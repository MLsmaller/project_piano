#-*- coding:utf-8 -*-

import cv2
import numpy as np
import os
from collections import Counter
import argparse

parser = argparse.ArgumentParser(description="检测图片中的钢琴区域")
parser.add_argument("--img_path", type=str, default="/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/",
                    help="需要检测的图片的路径")
parser.add_argument("--save_path", type=str, default="/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/res",
                    help="第一次裁剪后图片的存储路径")
parser.add_argument("--crop_path", type=str, default="/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/final",
                    help="第二次裁剪后图片的存储路径")
parser.add_argument("--thres", type=float, default=0.4,
                    help="判断钢琴区域内某一行上白色像素累计总数值")
parser.add_argument("--adjustNum", type=float, default=0.038,
                    help="是否对像素阈值进行调整")                       
parser.add_argument("--adj_light", type=float, default=0.5,
                    help="是否进行光照补偿")   
parser.add_argument("--binary_thres", type=int, default=180,
                    help="对图像二值化的阈值")
parser.add_argument("--gamma", type=int, default=0.5,
                        help="光照补偿系数,越小就越亮")                     
args = parser.parse_args()



file_list = [x for x in os.listdir(args.img_path) if x.endswith((".jpg", ".png"))]
file_list.sort(key=lambda x: int(x[:-4]))
img_list = [os.path.join(args.img_path, x) for x in file_list]
test_list = [os.path.join(args.img_path, x) for x in file_list if x.startswith("0003")] #--测试图片list

#-----将路径中原本存在的图片先删除
del_path = []
del_path.append(args.save_path)
del_path.append(args.crop_path)
for path in del_path:
    img_dir = [x for x in os.listdir(path) if x.endswith((".jpg", ".png"))]
    dirs = [os.path.join(path, x) for x in img_dir]
    for img in dirs:
        if os.path.isfile(img):
            os.remove(img)
#----如果视频一开始都有不包含手的视频比较好判断,从头遍历会遇到没手的,然后就选定那个矩形框,没有手的图片干扰会少很多
#----这种可以处理视频最后才出现手-

#----得到包含钢琴的矩形框------
def find_paino(img,img_path, save_path, crop_path,thres,binary_thres):

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)

    #-----检测图片-----
    print("\n")
    print(img_path)
    # img = cv2.imread(img_path)
    img_ori = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    width = img.shape[1]  #img.shape  [height(rows),width(cols),channels]
    height = img.shape[0]
    channels = img.shape[2]
    # print("the width,height,channels is {} {} {}".format(width,height,channels))

    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 200, 3)
    # cv2.imwrite("./canny1.jpg", edges)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 160)
    thetas = []
    xloc = []
    yloc = []
    pts = []
    if lines is not None:           #----首先要检测到直线
        for line in lines:
            rho,theta = line[0]  
            thetas.append(theta)
            if  (theta < (np.pi/4. )) or (theta > (3.*np.pi/4.0)): 
                pt1 = (int(rho/np.cos(theta)),0)
                pt2 = (int((rho-img_ori.shape[0]*np.sin(theta))/np.cos(theta)),img_ori.shape[0])
            else: 
                pt1 = (0,int(rho/np.sin(theta)))
                pt2 = (img_ori.shape[1], int((rho-img_ori.shape[1]*np.cos(theta))/np.sin(theta)))
                cv2.line(img_ori, pt1, pt2, (0, 255, 0), 1)
            xloc.append(pt1[0])
            yloc.append(pt1[1])
            pts.append((pt1, pt2))
            # print("直线的起点和终点坐标分别为{} 和 {}".format(pt1, pt2))

        cv2.imwrite("./test_hough1.jpg", img_ori)
        dic = dict(Counter(thetas))   #--Counter对list中的元素进行计数,返回元素及对应出现的次数
        x = [(key, value) for key, value in dic.items() if value > 1]

        if (len(x) > 0):     #----存在有平行的多组直线才进行后面的操作
            x.sort(key=lambda x: int(x[1]), reverse=True)  #---找到出现最多的一组直线
            obj_value = x[0][0]   
            obj_index = []

            for i,v in enumerate(thetas):
                if v == obj_value:
                    obj_index.append(i)          
            obj_yloc = [yloc[x] for x in obj_index]   #----目标直线(即平行直线)所对应的纵坐标
            new_pts = [pts[x] for x in obj_index]   #-----目标直线对应的起点和终点坐标
            new_loc = sorted(obj_yloc, key=lambda x: int(x))
            cv2.circle(img_ori, (10, 512), 7, (0, 0, 255), -1)
            cv2.imwrite("./darw.jpg", img_ori)
        
            min_loc = 0
            linesNum = 0    #----统计在图片下方的直线并且直线长度大于0.6*width的数量(霍夫变化)
            for k, loc in enumerate(obj_yloc):
                cur_pts = new_pts[k]
                dif = cur_pts[1][0] - cur_pts[0][0]
                if loc > 0.5 * height and dif > 0.6 * width:
                    linesNum += 1

            print("满足要求直线有{}条".format(linesNum))
            nums = 3       #符合要求的直线大于3条则认为是检测到钢琴了
            if (linesNum > nums):
                for loc in new_loc:
                    if loc > 0.5 * height:    #---取第一条大于0.5*h的直线作为上边界
                        min_loc = loc
                        break

                max_loc = max(new_loc)
                Rect1 = (0, min_loc, 0 + width, max_loc)
                # print("矩形框为: {}".format(Rect1))
                #-----先粗略的将钢琴图片裁剪出来(后续再根据像素精确的定位)
                crop_piano = img[Rect1[1]: Rect1[3], Rect1[0]: Rect1[2]]
                cv2.imwrite(os.path.join(save_path,os.path.basename(img_path)), crop_piano)
                #----将图像二值化,钢琴区域的像素较高,为255
                h, w, c = crop_piano.shape
                #-----光照补偿----
                # crop_piano = utils.light_enhance(crop_piano, 0.5)
                # crop_piano = crop_piano.astype(np.uint8)
                #-----opencv读取的图片类型是numpy,uint8(要转为uint8)-----
                gray_img = cv2.cvtColor(crop_piano, cv2.COLOR_BGR2GRAY)
                #----灰度图可以找连通区域??
                gray_img = cv2.medianBlur(gray_img, 5)
                _,res_img = cv2.threshold(gray_img, binary_thres, 255, cv2.THRESH_BINARY)
                cv2.imwrite("{}/gray_{}".format(save_path,os.path.basename(img_path)), res_img)

                loc1 = []
                loc2 = []
                #-----存在白色像素的行和列
                for i in range(h):
                    for j in range(w):
                        if int(res_img[i][j]) == 255:
                            loc1.append(i)
                            loc2.append(j) 
                loc1 = np.unique(loc1)    #-----y轴的坐标
                loc2 = np.unique(loc2)

                pixelnums = []
                #------统计每一行白色像素的数量
                for i in range(h):
                    num = 0
                    for j in range(w):
                        if i in loc1 and int(res_img[i][j]) == 255:
                            num += 1
                    if num > 0:
                        pixelnums.append(num)

                # print("选取的阈值为:{}".format(thres))
                findIndex = []
                thres = thres * w
                #-----白色像素的总量大于thres认为在钢琴区域内
                for j,index in enumerate(pixelnums):
                    if index > thres:
                        findIndex.append(j)
                
                temp_y = []
                for i in findIndex:
                    temp_y.append(loc1[i])
                # print("钢琴区域y轴的坐标有{}".format(temp_y))
                y_min = min(temp_y)   #钢琴左上角纵坐标
                y_max = max(temp_y)   #钢琴左下角纵坐标
                avg_loc = (y_max + y_min) / 2
                # print("y轴坐标最小最大值为{0} and {1}".format(y_min,y_max))

                temp_x = []
                #----找到左上角横坐标
                left_x = 0
                for i in range(h):
                    for j in range(w):
                        if i == y_min and int(res_img[i][j]) == 255:
                            left_x = j               #左上角横坐标
                            break
                    else:
                        continue
                    break
                #----找到右上角横坐标
                for i in range(h):
                    for j in range(w):
                        if i == avg_loc and int(res_img[i][j]) == 255:
                            temp_x.append(j)
                x_max = max(temp_x)
                
                left_x += 2  #---有些钢琴图片键盘比较倾斜,左上角坐标可以小一点包含稍微多一点
                crop_h = int(y_max - y_min)
                crop_w = int(x_max - left_x)
                Rect = (left_x, y_min, left_x + crop_w, y_min + crop_h)
                piano_img = crop_piano[Rect[1]:Rect[3], Rect[0]:Rect[2]]
                # cv2.rectangle(crop_piano, (left_x, y_min),(left_x + crop_w,y_min + crop_h), (0, 255, 0), 2)
                # cv2.imwrite(os.path.join(crop_path,os.path.basename(img_path)), crop_piano)
                
                # cv2.circle(crop_piano, (int(left_x), int(y_min)), 10, (0, 255, 0), -1)
                # cv2.circle(crop_piano, (int(left_x), int(y_max)), 10, (0, 255, 0), -1)
                # cv2.circle(crop_piano, (int(x_max), int(y_min)), 10, (0, 255, 0), -1)
                # cv2.imwrite("{}/draw_{}".format(save_path,os.path.basename(img_path)), crop_piano)
                
                return Rect,Rect1
            else:
                print("the img {} does not contain keyboard".format(img_path))
                return None, None
        else:
            return None,None
            
    else:
        print("该图片没有检测到直线")
        print("{} 不包含钢琴区域".format(img_path))
        return None,None

#----得到包含钢琴的矩形框------
def find_paino1(img,img_path, save_path, crop_path,thres,binary_thres):

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    if not os.path.exists(crop_path):
        os.mkdir(crop_path)

    #-----检测图片-----
    print("\n")
    print(img_path)
    # img = cv2.imread(img_path)
    img_ori = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    width = img.shape[1]  #img.shape  [height(rows),width(cols),channels]
    height = img.shape[0]
    channels = img.shape[2]
    # print("the width,height,channels is {} {} {}".format(width,height,channels))

    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 200, 3)
    # cv2.imwrite("./canny1.jpg", edges)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 160)
    thetas = []
    xloc = []
    yloc = []
    pts = []
    if lines is not None:           #----首先要检测到直线
        for line in lines:
            rho,theta = line[0]  
            thetas.append(theta)
            if  (theta < (np.pi/4. )) or (theta > (3.*np.pi/4.0)): 
                pt1 = (int(rho/np.cos(theta)),0)
                pt2 = (int((rho-img_ori.shape[0]*np.sin(theta))/np.cos(theta)),img_ori.shape[0])
            else: 
                pt1 = (0,int(rho/np.sin(theta)))
                pt2 = (img_ori.shape[1], int((rho-img_ori.shape[1]*np.cos(theta))/np.sin(theta)))
                cv2.line(img_ori, pt1, pt2, (0, 255, 0), 1)
            xloc.append(pt1[0])
            yloc.append(pt1[1])
            pts.append((pt1, pt2))
            # print("直线的起点和终点坐标分别为{} 和 {}".format(pt1, pt2))

        cv2.imwrite("./test_hough1.jpg", img_ori)
        dic = dict(Counter(thetas))   #--Counter对list中的元素进行计数,返回元素及对应出现的次数
        x = [(key, value) for key, value in dic.items() if value > 1]

        if (len(x) > 0):     #----存在有平行的多组直线才进行后面的操作
            x.sort(key=lambda x: int(x[1]), reverse=True)  #---找到出现最多的一组直线
            obj_value = x[0][0]   
            obj_index = []

            for i,v in enumerate(thetas):
                if v == obj_value:
                    obj_index.append(i)          
            obj_yloc = [yloc[x] for x in obj_index]   #----目标直线(即平行直线)所对应的纵坐标
            new_pts = [pts[x] for x in obj_index]   #-----目标直线对应的起点和终点坐标
            new_loc = sorted(obj_yloc, key=lambda x: int(x))
            cv2.circle(img_ori, (10, 512), 7, (0, 0, 255), -1)
            cv2.imwrite("./darw.jpg", img_ori)
        
            min_loc = 0
            linesNum = 0    #----统计在图片下方的直线并且直线长度大于0.6*width的数量(霍夫变化)
            for k, loc in enumerate(obj_yloc):
                cur_pts = new_pts[k]
                dif = cur_pts[1][0] - cur_pts[0][0]
                if loc > 0.5 * height and dif > 0.6 * width:
                    linesNum += 1

            print("满足要求直线有{}条".format(linesNum))
            nums = 3       #符合要求的直线大于3条则认为是检测到钢琴了
            if (linesNum > nums):
                for loc in new_loc:
                    if loc > 0.5 * height:    #---取第一条大于0.5*h的直线作为上边界
                        min_loc = loc
                        break

                max_loc = max(new_loc)
                Rect1 = (0, min_loc, 0 + width, max_loc)
                # print("矩形框为: {}".format(Rect1))
                #-----先粗略的将钢琴图片裁剪出来(后续再根据像素精确的定位)
                crop_piano = img[Rect1[1]: Rect1[3], Rect1[0]: Rect1[2]]
                cv2.imwrite(os.path.join(save_path,os.path.basename(img_path)), crop_piano)
                #----将图像二值化,钢琴区域的像素较高,为255
                h, w, c = crop_piano.shape
                #-----光照补偿----
                crop_piano = light_enhance(crop_piano, 0.5)
                crop_piano = crop_piano.astype(np.uint8)
                #-----opencv读取的图片类型是numpy,uint8(要转为uint8)-----
                gray_img = cv2.cvtColor(crop_piano, cv2.COLOR_BGR2GRAY)
                #----灰度图可以找连通区域??
                gray_img = cv2.medianBlur(gray_img, 5)
                _,res_img = cv2.threshold(gray_img, binary_thres, 255, cv2.THRESH_BINARY)
                cv2.imwrite("{}/gray_{}".format(save_path,os.path.basename(img_path)), res_img)

                loc1 = []
                loc2 = []
                #-----存在白色像素的行和列
                for i in range(h):
                    for j in range(w):
                        if int(res_img[i][j]) == 255:
                            loc1.append(i)
                            loc2.append(j) 
                loc1 = np.unique(loc1)    #-----y轴的坐标
                loc2 = np.unique(loc2)

                pixelnums = []
                #------统计每一行白色像素的数量
                for i in range(h):
                    num = 0
                    for j in range(w):
                        if i in loc1 and int(res_img[i][j]) == 255:
                            num += 1
                    if num > 0:
                        pixelnums.append(num)

                # print("选取的阈值为:{}".format(thres))
                findIndex = []
                thres = thres * w
                #-----白色像素的总量大于thres认为在钢琴区域内
                for j,index in enumerate(pixelnums):
                    if index > thres:
                        findIndex.append(j)
                
                temp_y = []
                for i in findIndex:
                    temp_y.append(loc1[i])
                # print("钢琴区域y轴的坐标有{}".format(temp_y))
                y_min = min(temp_y)   #钢琴左上角纵坐标
                y_max = max(temp_y)   #钢琴左下角纵坐标
                avg_loc = (y_max + y_min) / 2
                # print("y轴坐标最小最大值为{0} and {1}".format(y_min,y_max))

                temp_x = []
                #----找到左上角横坐标
                left_x = 0
                for i in range(h):
                    for j in range(w):
                        if i == y_min and int(res_img[i][j]) == 255:
                            left_x = j               #左上角横坐标
                            break
                    else:
                        continue
                    break
                #----找到右上角横坐标
                for i in range(h):
                    for j in range(w):
                        if i == avg_loc and int(res_img[i][j]) == 255:
                            temp_x.append(j)
                x_max = max(temp_x)
                
                left_x += 2  #---有些钢琴图片键盘比较倾斜,左上角坐标可以小一点包含稍微多一点
                crop_h = int(y_max - y_min)
                crop_w = int(x_max - left_x)
                Rect = (left_x, y_min, left_x + crop_w, y_min + crop_h)
                piano_img = crop_piano[Rect[1]:Rect[3], Rect[0]:Rect[2]]
                # cv2.rectangle(crop_piano, (left_x, y_min),(left_x + crop_w,y_min + crop_h), (0, 255, 0), 2)
                # cv2.imwrite(os.path.join(crop_path,os.path.basename(img_path)), crop_piano)
                
                # cv2.circle(crop_piano, (int(left_x), int(y_min)), 10, (0, 255, 0), -1)
                # cv2.circle(crop_piano, (int(left_x), int(y_max)), 10, (0, 255, 0), -1)
                # cv2.circle(crop_piano, (int(x_max), int(y_min)), 10, (0, 255, 0), -1)
                # cv2.imwrite("{}/draw_{}".format(save_path,os.path.basename(img_path)), crop_piano)
                
                return Rect,Rect1
            else:
                print("the img {} does not contain keyboard".format(img_path))
                return None, None
        else:
            return None,None
            
    else:
        print("该图片没有检测到直线")
        print("{} 不包含钢琴区域".format(img_path))
        return None,None

#-----判断是否需要调整每行像素的阈值(如果钢琴左右边缘离边界比较远)
def adjust_thres(Rect, Rect1, adjustNum):
    width = Rect1[2] - Rect1[0]
    print("width is {}".format(width))
    value = float(Rect[0]) / float(width)
    #-----钢琴键盘矩形框左上角坐标占图片宽度的比例大于0.038就将阈值调小一点,每一行累计的像素值少一点---
    if value > adjustNum:
        return True
    else:
        return False

#-----判断是否需要调整光照和二值化阈值(针对光照条件不太好的情况)
def adjust_light(Rect, Rect1, adj_light):
    height_paino = Rect[3] - Rect[1]    #----钢琴box的高度
    height_crop = Rect1[3] - Rect1[1]     #---霍夫变化box的高度
    ratio = float(height_paino) / float(height_crop)
    #-----检测到的钢琴键盘高度占比小于整个裁剪图像的0.5,则认为检测不完全,光照补偿---
    if ratio < adj_light:
        return True
    else:
        return False

#-------光照补偿,使得图片变得亮一点----
def light_enhance(img, gamma):
    img = img.astype(np.float32)
    h, w, c = img.shape
    #----让图像矩阵中每一个像素值都乘以自己的次幂-----
    temp_img = [[[img[i][j][k]**gamma for k in range(c)] for j in range(w)] for i in range(h)]
    temp_img = np.array(temp_img)    #---listToarray
    final = cv2.normalize(temp_img, None, 0, 255, cv2.NORM_MINMAX, -1) #---归一化
    return final 

#----光线不好的一般都是那种就是中间的那几个黑键会连在一起，然后就只框到了下面的区域,可以判断如果Rect的height太小的话可以采取小一点的阈值来试一下看看???
#---模型训练的时候可以对图片做预处理,比如变亮变暗还有光照啊模糊各种之类的
if __name__ == "__main__":
    
    Rectlist = []
    Tostop = 1000
    frames = 0
    for img_path in img_list:
    # for img_path in test_list:
        img = cv2.imread(img_path)
        img1 = np.zeros(img.shape, np.uint8)
        img1 = img.copy()
        Rect, Rect1 = find_paino(img, img_path, args.save_path, args.crop_path,
                                 args.thres,args.binary_thres)
        #----Rect1是用于判断是否调整像素阈值的0.0
        if Rect is not None:
            Rectlist.append(Rect)
            flag = adjust_thres(Rect, Rect1, args.adjustNum)
            #----判断是否调整每行的积累的阈值
            new_thres = 0.35
            if flag:
                print("adjust")
                Rect, Rect1 = find_paino(img, img_path, args.save_path, args.crop_path,
                                         new_thres,args.binary_thres)  
        
            light = adjust_light(Rect, Rect1, args.adj_light)
            #----判断是否调整光照强度
            if light:
                print("light")
                # img = light_enhance(img, args.gamma)
                # img = img.astype(np.uint8)
                #-----先进行霍夫变化在调整光照(只对二值化有作用)
                new_light = 130
                Rect, Rect1 = find_paino1(img, img_path, args.save_path, args.crop_path,
                                         new_thres,new_light)
            #----画图观察
            crop_piano = img1[Rect1[1]:Rect1[3], Rect1[0]:Rect1[2]]  #----霍夫变化得到的裁剪图像
            cv2.rectangle(crop_piano, (Rect[0], Rect[1]), (Rect[2], Rect[3]), (0, 255, 0), 2)
            cv2.imwrite(os.path.join(args.crop_path,os.path.basename(img_path)), crop_piano)
        
        print("矩形框为{}".format(Rect))
        frames += 1
        if (frames > Tostop):
            break
         
    dicRect = dict(Counter(Rectlist))   #-----统计出现最多次数的矩形框作为最终的Rect
    x = [(key, value) for key, value in dicRect.items() if value > 1]
    if (len(x) > 0):   
        x.sort(key=lambda x: int(x[1]), reverse=True)
        Rect=x[0][0]
    print("最终的Rect为{}".format(Rect))
    

    

    #-----视频转换过程中的时候有可能有几张图片比较模糊,比较白,框的不一样,需要进行判断一下
    #---可以统计所有帧中出现最多的一个box

