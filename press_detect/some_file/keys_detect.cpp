#include<string>
#include<iostream>
#include<fstream>
#include<vector>
#include<numeric>
#include<cmath>
#include<opencv2/opencv.hpp>
#include<bwlabel.hpp>
#include<get_keyboard.hpp>
using namespace std;
using namespace cv;

void illumination(Mat &src,Mat &overlay,const int &stepsize){
	int width = src.cols;
	int height = src.rows;  
	int v;
	int pixelSize = src.channels();    //每个像素多少个字节
	int linesize = width * pixelSize;  //每一行需要这么多字节存储
	vector<vector<int>>num(height,vector<int>(linesize,0));  //存放v
	for (int i = 0; i < height; i++)
	{
		uchar *data1=src.ptr<uchar>(i);
		uchar *data2=overlay.ptr<uchar>(i);
		for (int j = 0; j < linesize; j++)
		{
			v = int(data2[j]-data1[j]);
			num[i].push_back(v);
			//cout<<v<<endl; //
			if (v > 0)
			{

				data1[j] += uchar((stepsize < v) ? stepsize : v);

			}
			else if (v < 0) {
				v = -v;
				data1[j] -= uchar((stepsize < v) ? stepsize : v);
			}
		}
	}
}


int main(int argc, char *argv[])
{
	int nums = 0;
	while(1){
		nums++;
		if(nums>1)     //控制循环多少次
			break; 
		Mat src,src_rgb, src_rgb1;
		string save_path = "/home/lj/cy/tf/handtracking/img_tm/";
		Directory dir;     //Directory类,对文件进行操作
		string extent=".jpg";
		vector<string> FileLists = dir.GetListFiles(save_path,extent,true); //true则返回的为绝对路径,false为文件名
		char img_path[80];

		Mat base=imread(save_path+FileLists[0]);
		vector<Rect>box_hand1;
		base = keyboard(base,box_hand1);
		Mat img_ori=base.clone();
		cvtColor(base,base,CV_BGR2GRAY);
		int b_width=base.size().height;
		int b_height=base.size().width;
		string test_path = "/home/lj/cy/openpose/piano/test_piano/res/test_background/";
		int frames=0;
		vector<Rect>black_box;
		vector<double>white_loc;
		Mat baseTotest=base.clone();
		key_loc(baseTotest,black_box,white_loc);

		for(size_t i=650;i<660;i++){    //750.760可以??
			string img_name=FileLists[i];
			sprintf(img_path,"%s%s",save_path.c_str(),img_name.c_str());
			src_rgb = imread(img_path);   
			if (src_rgb.empty())
				exit(-1);
			Mat img_keyboard;
			vector<Rect>box_hand;
			img_keyboard = keyboard(src_rgb,box_hand);
			cvtColor(img_keyboard,img_keyboard,CV_BGR2GRAY);
			int stepsize=60;
			illumination(img_keyboard,base,stepsize);
			imwrite("../illumi.jpg",img_keyboard);
			imwrite("../illumi_1.jpg",base);
			Mat black(b_width,b_height,CV_8UC1);   //detect blackkey.
			Mat white=black.clone();              //detect whitekey
			int threshold=20;   
			for(int i=0;i<b_width;i++)
			{
				uchar *data1=base.ptr<uchar>(i);
				uchar *data2=img_keyboard.ptr<uchar>(i);
				uchar *data3=black.ptr<uchar>(i);
				uchar *data4=white.ptr<uchar>(i);
				for(int j=0;j<b_height;j++)      //对于彩色图,还要乘以3(相当于R,G,B平铺开来,每个都是width×height);
				{	
					if((data2[j]-data1[j])>threshold){
						data3[j]=255;
					}
					else{
						data3[j]=0;
					}
					if((data1[j]-data2[j])>threshold){  
						data4[j]=255;
					}
					else{
						data4[j]=0;
					}
				}
			}
			char buf1[80];
			char buf2[80];
			sprintf(buf1,"%sneg_%d.jpg",test_path.c_str(),frames);
			imwrite(buf1,black);
			sprintf(buf2,"%spos_%d.jpg",test_path.c_str(),frames);
			imwrite(buf2,white); 
			frames++;
		}




		/*
		Mat result;
		Rect rct;
		rct=keyboard_box(src_temp, result, box,rct);  //检测出矩形框区域
		Mat img_rgb = Mat(src_rgb1, rct);  //得到彩色图像
		imshow("img_rgb", img_rgb);
		//imshow("2", result);
		result = remove_region(result);    //去除一些像素点
		imshow("3", result);

		vector<vector<Point>> blackkey_num;
		Mat imageContours = Mat::zeros(result.size(), CV_8UC1);  //绘制轮廓
		blackkey_num = k_num(result,imageContours);    //得到黑键的轮廓

		cout << "筛选出的轮廓(黑键)数量" << blackkey_num.size() << endl;
		imshow("5", imageContours);

		int width = rct.width;
		int height = rct.height;
		int keyNum = 52;
		int keywidth = width / keyNum;
		for (int i = 0; i <= keyNum; i++)
		{
			line(img_rgb, Point2f(float(i*keywidth), float(0)), Point2f(float(i*keywidth), float(width)), Scalar(0,0,255), 1, 8);

		}
		imshow("6", img_rgb);

		//-----------因为黑键框的大小都差不多，因此可以通过判断轮廓内的像素点总数是否在某一区间内来判断黑键的数量
		//有黑键按下时会让一些区域连通或者减少啥的，因此可以取轮廓数量最多的作为背景
		//黑键长度是整个钢琴的2/3长
		
		Size rec = result.size();
		*/
	}

	return 0;
}