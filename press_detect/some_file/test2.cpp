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

//-----相邻帧之间进行相减
string save_path = "/home/lj/cy/openpose/some_code/video_to_image/res/test2/";
Directory dir;     
string extent=".jpg";
vector<string> FileLists = dir.GetListFiles(save_path, ".jpg", false); //true则返回的为绝对路径,false为文件名
char img_path[80];
string test_path = "/home/lj/cy/openpose/piano/test_piano/res/test_background1/";
int frames=0;
string black_path = "/home/lj/cy/openpose/piano/test_piano/res/line_black/";
char buf_save[80];
int main(int argc, char *argv[])
{
	Mat src,src_rgb;
	Mat base=imread(save_path+FileLists[150]);
	cout<<"the name of base img is "<<save_path+FileLists[150]<<endl;
	Mat img_ori=base.clone();
	cvtColor(base,base,CV_BGR2GRAY);
	int b_width=base.size().height;
	int b_height=base.size().width;
	vector<Rect>black_box;
	vector<double>white_loc;
	vector<int>area; 
	Mat baseTotest=base.clone();
	key_loc(baseTotest,black_box,white_loc,area);

	for(size_t i=1100;i<1105;i++){     
		string img_name=FileLists[i];
		cout<<img_name<<endl;
		sprintf(img_path,"%s%s",save_path.c_str(),img_name.c_str());

        string img_name1=FileLists[i+1];
        char img_path1[80];
		sprintf(img_path1,"%s%s",save_path.c_str(),img_name1.c_str());
		Mat src_rgb1 = imread(img_path1);
		cvtColor(src_rgb1,src_rgb1,CV_BGR2GRAY);

		src_rgb = imread(img_path);  
		if (src_rgb.empty())
			exit(-1);
		Mat img_keyboard=src_rgb.clone();
		cvtColor(img_keyboard,img_keyboard,CV_BGR2GRAY);

        Mat img1=src_rgb1-img_keyboard;
        Mat img3=img_keyboard-src_rgb1;
		char buf3[80];
		sprintf(buf3,"%stest_%d.jpg",test_path.c_str(),frames);
		imwrite(buf3,img1);

		Mat black(b_width,b_height,CV_8UC1);   //detect blackkey.
		Mat white=black.clone();              //detect whitekey
		int threshold=20;    
		for(int i=0;i<b_width;i++)
		{
			uchar *data1=src_rgb1.ptr<uchar>(i);
			uchar *data2=img_keyboard.ptr<uchar>(i);
			uchar *data3=black.ptr<uchar>(i);
			uchar *data4=white.ptr<uchar>(i);
			for(int j=0;j<b_height;j++)     
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
	return 0;
}