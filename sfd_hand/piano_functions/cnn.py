#-*- coding:utf-8 -*- 
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import cv2
import os
import argparse


base_path = "/home/data/cy/projects/piano/KJnotes/frames1/crop_img/3638.jpg"
test_path = "/home/data/cy/projects/piano/KJnotes/frames1/crop_img/0266.jpg"


if __name__ == "__main__":
    base_img = cv2.imread(base_path)
    cur_img = cv2.imread(test_path)
    print(cur_img.shape)
    base_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    cur_img = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
    dif_img = cur_img - base_img
    differ = cv2.absdiff(base_img, cur_img)

    cv2.imwrite("./differ.jpg", differ)

