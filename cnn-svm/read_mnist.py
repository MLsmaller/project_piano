#-*- coding:utf-8 -*-
import cv2 
import os
import numpy as np
import struct

path = os.getcwd()
data_path=os.path.join(path,"MNIST_data")

def load_mnist(path, kind='train'):
    labels_path = os.path.join(path, "{}-labels-idx1-ubyte".format(kind))
    images_path = os.path.join(path, "{}-images-idx3-ubyte".format(kind))

    with open(labels_path, 'rb') as lbpath:
        magic, n = struct.unpack('>II', lbpath.read(8))   #---struct.pack()将python的值根据格式符转换为字符串(字节流),eg a=20,str=struct.pack("i",a)
        
        labels = np.fromfile(lbpath, dtype=np.uint8)   #---np.fromfile(filename/string,dtype)读取数据
        
    with open(images_path, 'rb') as imgpath:
        magic, num, rows, cols = struct.unpack('>IIII', imgpath.read(16))    #---struct.unpack()将字节流(字符串)转换为python类型,egI表示无符号整形,(4个字节)
        
        images = np.fromfile(imgpath, dtype=np.uint8).reshape(len(labels), 784)  #mnist中每张图大小是28x28，将其展开为一个一维的行向量,每一行即
                                                                                 #一张图片,每行784个值(像素)
    return images, labels
    

if __name__ == "__main__":
    images, labels = load_mnist(data_path, "train")
    print(len(labels))
    print(type(images))
    print(images.shape)
    