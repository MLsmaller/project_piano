#-*- coding:utf-8 -*_
import os
import numpy


#-------将目录下的图片路径逐行读入txt文件中-----------
path = os.getcwd()
img_path = os.path.join(path, "res/video/white")
img_list = [os.path.join(img_path, x) for x in os.listdir(img_path) if x.endswith(".jpg")]

txt_file = "realdata.txt"
txt_path = os.path.join(path, txt_file)
if os.path.exists(txt_path):
    os.remove(txt_path)

obj = open(txt_path, 'w')
for img in img_list:
    obj.writelines(img)
    obj.writelines('\n')        #每次写入一个路径之后再写一个换行符
obj.close()
print("the txt file has done")


