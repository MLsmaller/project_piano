#-*- coding:utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import os,random
import numpy as np
import json,math
import argparse
import struct, midi
import sys

black_num = [2, 5, 7, 10, 12, 14, 17, 19, 22, 24, 26, 29, 31, 34, 36, 38, 41, 43,
            46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79,82, 84, 86]
white_num = []
for i in range(1, 89):
    if i not in black_num:
        white_num.append(i)
# print(white_num)

#-----设置为函数之后这样别的函数调用时就不会影响别的parser参数
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_Savepath", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/video2.avi",
                        help="要生成的视频路径")
    parser.add_argument("--fps", type=int, default=20,
                        help="the fps of video")
    parser.add_argument("--img_path", type=str, default="/home/data/cy/projects/piano/KJnotes/frames2/res_img",
                        help="图片的存储途径")
    parser.add_argument("--midi_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/02级_04_二月里来.mid",
                        help="需要解析的midi文件的路径")
    parser.add_argument("--w_txt_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/txt/w_frame2.txt",
                        help="将midi文件中读取到的白键和时间信息存储为txt文件")                                                
    parser.add_argument("--b_txt_path", type=str, default="/home/data/cy/projects/piano/KJnotes/midi/txt/b_frame2.txt",
                        help="将midi文件中读取到的黑键和时间信息存储为txt文件")           
    parser.add_argument("--test_path", type=str, default="/home/data/cy/projects/piano/initial_video/frame/video1_whole_frame/0000.jpg",
                        help="用以测试的图片 ")
    parser.add_argument("--gamma", type=int, default=0.5,
                        help="光照补偿系数,越小就越亮")
    args = parser.parse_args()
    return args
    
#-----用以生成视频,可观察一下检测的效果-----
def form_video(img_path, fps,video_Savepath):
    img_list = os.listdir(img_path)
    img_list.sort(key=lambda x: int(x[:-4]))   #----对图片进行排序,是对os.listdir()得到的结果eg:0621.jpg
    img_list1 = [os.path.join(img_path, x) for x in img_list]
    picknumber = 1
    sample = random.sample(img_list1, picknumber)
    img_str = "".join(sample)
    img_one = cv2.imread(img_str)
    h, w, c = img_one.shape   #---shape: h,w,c
    img_size = (w, h)
    
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    if os.path.exists(video_Savepath):
        os.remove(video_Savepath)
    videoWriter = cv2.VideoWriter(video_Savepath, fourcc, fps, img_size)
    for path in img_list1:
        print(path)
        img = cv2.imread(path)
        videoWriter.write(img)
    videoWriter.release()
    print(w,h)
    print("the video {} has done ".format(video_Savepath))


#----读取mid文件存为时间与按键相对应的txt文件---
def parse_midi(midi_path,w_txt_path,b_txt_path):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    pattern = midi.read_midifile(midi_path)
    #-----data[pitch,velocity]
    tickLength = None

    for track in pattern:
        for event in track:
            if isinstance(event, midi.SetTempoEvent):  #---设置速度事件----,isinstance用以判断类型
                tickLength = 60./event.bpm/pattern.resolution    #----现在one tick 代表tickLength(s)
                print(event.bpm)    #bpm(beat per minute)每分钟多少拍
                print("now one tick represents {0} s".format(tickLength))    #--0.001157s
                break
        else:            #--for else 加上 break可用于跳出二重循环
            continue
        break
            #print(event)   #---<class 'midi.events.NoteOnEvent'>
            #print(e.__class__.__name__)   #---NoteOnEvent---
    def getSeconds(tick):
        return tickLength*tick 
    pre_keys = []
    pre_times = []
    pass_index = []
    keys = []
    
    Tostop = 0
    threshold = 1000
    #----第一次循环为右手的,第二次为左手--
    for track in pattern:
        track = list(track)
        t = 0
        for i,event in enumerate(track):
            #print(event)
            if isinstance(event, midi.NoteOnEvent):
                if i in pass_index:
                    t += event.tick
                    continue
                Tostop += 1
                octave, note = divmod(event.pitch, 12)  #---divmod的结果包括除数和余数eg:divmod(10,3)=(3,1)
                octave = octave - 1 
                # print('Note {}{} plays at {:.02f} seconds'.format(notes[note],
                                #  octave, getSeconds(event.tick)))
                #print("{0} and {1}".format(octave, note))
                key_num = 4 + (octave-1) * 12 + note
                # print("按键编号为: {}".format(key_num))      #--连着按下两个相同的键的时候后面的tick不一样,第一个tick是1一般,除了最开始的NoteOnEvent

                t += event.tick
                pre_keys.append(key_num)
                cur_time = getSeconds(t)
                pre_times.append(cur_time)
                keys.append((cur_time, key_num))
                
                print("cur_time is {} s".format(cur_time))
                print(event)
                print("\n")
                
                cur_pitch = event.pitch
                step = 0
                #------找到与当前按键成对的一个NoteOnEvent事件并记录其下标----
                for j in range(i + 1, len(track)):
                    if isinstance(track[j], midi.NoteOnEvent):
                        next_event = track[j]
                        if (next_event.pitch == cur_pitch):
                            step += 1
                            pass_index.append(i + step)
                            break
                        else:
                            step += 1
                    else:
                        step += 1
                #print("下一个对应的下标为: {}, event: {}".format(i+step,track[i+step]))
                print("与当前按键对应的事件为{}".format(track[i + step]))
                if Tostop > threshold:
                    break
            else:
                t += event.tick
                if event.tick is not 0:
                    print("{} 不是一个NoteOnEvent事件".format(event))
        #break
        print("这是分隔线-------------------------------------------------------------")
    
    keys.sort(key=lambda x: (float(x[0]),int(x[1])))  #----sort()函数先按照横坐标排序再按照纵坐标排序
    if os.path.exists(w_txt_path):
        os.remove(w_txt_path)
    if os.path.exists(b_txt_path):
        os.remove(b_txt_path)

    w_fout = open(w_txt_path, 'w')   #----存储白键的txt
    b_fout = open(b_txt_path, 'w')   #----存储黑键的txt
    for index, key in enumerate(keys):
        #print(key)
        press = int(key[1])
        if press in black_num:
            Bkey_index = black_num.index(press) + 1
            press = int(Bkey_index)
            b_fout.write("{} ".format(key[0]))
            b_fout.write("{}".format(press))
            b_fout.write("\n")
        else:
            Wkey_index = white_num.index(press) + 1
            press = int(Wkey_index)
            w_fout.write("{} ".format(key[0]))
            w_fout.write("{}".format(press))
            w_fout.write("\n")
    
    w_fout.close()
    b_fout.close()
    print("The w_txt_path {} and b_txt_path {} has done".format(w_txt_path,b_txt_path))
    #-----pattern中第一个track记录的是右手的pitch按键,第二个是左手的

    #----问一下学长那个以前弄过的那个乐谱跟踪的东西
    #---12个键一个周期,5个黑键和7个白键----,从第一个键开始
    #---36+52=88  按键是21-108,  pitch除以12的余数为0-11,对应一个周期内的12个按键,即C,C#,D...
    #--------------------------  pitch除以12的商表示当前按键pitch在哪个八度(octave)内


#-------光照补偿,使得图片变得亮一点----
def light_enhance(img, gamma):
    img = img.astype(np.float32)
    h, w, c = img.shape
    #----让图像矩阵中每一个像素值都乘以自己的次幂-----
    temp_img = [[[img[i][j][k]**gamma for k in range(c)] for j in range(w)] for i in range(h)]
    temp_img = np.array(temp_img)    #---listToarray
    final = cv2.normalize(temp_img, None, 0, 255, cv2.NORM_MINMAX, -1) #---归一化
    return final 

if __name__=="__main__":
    #form_video(args.img_path, args.fps, args.video_Savepath)
    # parse_midi(args.midi_path, args.w_txt_path,args.b_txt_path)
    args = parser()
    img = cv2.imread(args.test_path)
    final = light_enhance(img, args.gamma)
    cv2.imwrite("./normal.jpg", final)
    