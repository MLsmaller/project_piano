#-*- coding:utf-8 -*-
import torch
import torch.nn as nn
from torch.autograd import Variable
# from model.ResNet import ResNet18
import torch.utils.data as Data

import torchvision.transforms as transforms
import cv2 
import numpy as np
import torch.nn.functional as F
import os
import argparse
from PIL import Image

# os.environ['CUDA_VISIBLE_DEVICES'] = '3'

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_classes', type=int, default=2,
                        help="分类数目")
    parser.add_argument('--test_path', type=str, default="./test_imgs/keys_imgs/level_1_no_3/1/",
                        help="测试图片目录")
    parser.add_argument('--model_name', type=str, default="/home/data/cy/projects/piano/weights/keys/keys_900_torch0.3.pth",
                        help="模型名称")
    parser.add_argument('--gpu_ids', type=str, default="2,3",
                        help="gpu id ")                     
    args=parser.parse_args()
    return args
    
model_dir = "/home/data/cy/projects/classification/keys/weights"
num_class = []
num_class.append('unpress')
num_class.append('press')
    
# test_list = os.listdir(args.test_path)
# img_list = [os.path.join(args.test_path, x) for x in test_list]
# img_list.sort(key=lambda x: str(x))

class ResidualBlock(nn.Module):
    def __init__(self,inchannels,outchannels,stride = 1,need_shortcut = False):
        super(ResidualBlock,self).__init__()
        self.right = nn.Sequential(
            nn.Conv2d(inchannels,outchannels,kernel_size = 3,stride = stride,padding = 1),
            nn.BatchNorm2d(outchannels),
            nn.ReLU(True),
            nn.Conv2d(outchannels,outchannels,kernel_size = 3,stride = 1,padding = 1),
            nn.BatchNorm2d(outchannels)
         )
        if need_shortcut:
            self.short_cut = nn.Sequential(
                nn.Conv2d(inchannels,outchannels,kernel_size = 1,stride = stride),
                nn.BatchNorm2d(outchannels)
            )
        else:
            self.short_cut = nn.Sequential()
    
    def forward(self,x):
        out = self.right(x)
        out += self.short_cut(x)
        return F.relu(out)

class ResNet18(nn.Module):
    def __init__(self, num_classes):
        super(ResNet18,self).__init__()
        self.pre_layer = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3), #---灰度图
            # nn.Conv2d(3,64,kernel_size=7,stride=2,padding=3),    #---rgb图
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=3,stride=2)
        )
        self.block_1 = ResidualBlock(64,64,stride=1,need_shortcut=True)
        self.block_2 = ResidualBlock(64,64,stride=1,need_shortcut=False)
        self.block_3 = ResidualBlock(64,128,stride=2,need_shortcut=True)
        self.block_4 = ResidualBlock(128,128,stride=1,need_shortcut=False)
        self.block_5 = ResidualBlock(128,256,stride=2,need_shortcut=True)
        self.block_6 = ResidualBlock(256,256,stride=1,need_shortcut=False)
        self.block_7 = ResidualBlock(256,512,stride=2,need_shortcut=True)
        self.block_8 = ResidualBlock(512,512,stride=1,need_shortcut=False)
        self.avepool = nn.AvgPool2d(kernel_size=7,stride=1)
        self.fc = nn.Linear(512,num_classes)
        self.num_classes = num_classes

    def forward(self,x):
        out = self.pre_layer(x)
        out = self.block_2(self.block_1(out))
        out = self.block_4(self.block_3(out))
        out = self.block_6(self.block_5(out))
        out = self.block_8(self.block_7(out))
        out = self.avepool(out)
        out = out.view(-1,self.num_flatters(out))
        return self.fc(out)

    def num_flatters(self,x):
        sizes = x.size()[1:]
        result = 1
        for size in sizes:
            result *= size
        return result 

def detect_keys(img,model_name):
    #----训练时用了nn.DataParallel(),测试的时候也用上
    model = ResNet18(2)   #---resnet
    model_path = os.path.join(model_dir, model_name)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    model = model.cuda()


    img = img.convert('P')
    assert (img is not None), "error read img"
    tensor = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor()])

    img = tensor(img)
    img = img.unsqueeze(0)  
    
    img = img.cuda()

    output = model(img)
    prob = F.softmax(output, dim=1)   #----按行softmax,行的和概率为1,每个元素代表着概率
    prob = Variable(prob)
    prob = prob.cpu().numpy()
    pred = np.argmax(prob, 1)
    index = pred.item()
    print("最有可能的类为: {}".format(num_class[index]))
    return index
      


if __name__ == "__main__":
    args = parser()
    img_path = '/home/data/cy/projects/piano/data/train/test_dir/level_1_no_2'
    img_list = [os.path.join(img_path, x) for x in os.listdir(img_path)]
    for path in img_list:
        img=Image.open(path)
        detect_keys(img)