#include<opencv2/opencv.hpp>
#include<iostream>
#include<string>
#include<vector>
#include <iomanip> 
#include <cstdio>
#include <sstream>
#include <fstream>
#include<json/json.h>
#include<ctime>
#include<cmath>

using namespace  cv;
using namespace std;
//using std::string;

//全局变量
Mat inputImage,base;   
int width, height , keyNum=52;
int maxvalue = 255, maxcount = 300, count_threshold_w = 15;
int count_threshold_b = 10, value_threshold_w =10, value_threshold_b = 30;
int frames = 0;
int fps = 50;  

vector<vector<bool>> pressed(keyNum + 1, vector<bool>(2, false));
//video_path
string videopath = "/home/cy/openpose/piano/Music-Transcription/data/ksc_light2.mp4";
VideoCapture capture(videopath);  //打开视频文件
vector<Point> pts;

float dist(Point p, Point q)
{
	return sqrt((p.x - q.x)*(p.x - q.x) + (p.y - q.y)*(p.y - q.y));
}

vector<Point2f>readJson(string &buff){   
	vector<Point2f>finger_loc(10);
	Json::Reader reader;
	Json::Value root;  
	ifstream in;  

	in.open(buff.c_str(), ios::binary);
	if(!in.is_open()){
		cout<<"Error opening file\n";
	}

	if (reader.parse(in, root)){

		finger_loc[0] = Point2f(root["people"][0U]["hand_left_keypoints_2d"][20 * 3].asDouble(), root["people"][0U]["hand_left_keypoints_2d"][20 * 3+1].asDouble());  //左小指
		finger_loc[1] = Point2f(root["people"][0U]["hand_left_keypoints_2d"][16 * 3].asDouble(), root["people"][0U]["hand_left_keypoints_2d"][16 * 3 + 1].asDouble()); 
		finger_loc[2] = Point2f(root["people"][0U]["hand_left_keypoints_2d"][12 * 3].asDouble(), root["people"][0U]["hand_left_keypoints_2d"][12 * 3 + 1].asDouble());
		finger_loc[3] = Point2f(root["people"][0U]["hand_left_keypoints_2d"][8 * 3].asDouble(), root["people"][0U]["hand_left_keypoints_2d"][8 * 3 + 1].asDouble());
		finger_loc[4] = Point2f(root["people"][0U]["hand_left_keypoints_2d"][4 * 3].asDouble(), root["people"][0U]["hand_left_keypoints_2d"][4 * 3 + 1].asDouble()); //左大拇指


		finger_loc[5] = Point2f(root["people"][0U]["hand_right_keypoints_2d"][4 * 3].asDouble(), root["people"][0U]["hand_right_keypoints_2d"][4 * 3 + 1].asDouble());  //右大拇指
		finger_loc[6] = Point2f(root["people"][0U]["hand_right_keypoints_2d"][8 * 3].asDouble(), root["people"][0U]["hand_right_keypoints_2d"][8 * 3 + 1].asDouble());
		finger_loc[7] = Point2f(root["people"][0U]["hand_right_keypoints_2d"][12 * 3].asDouble(), root["people"][0U]["hand_right_keypoints_2d"][12 * 3 + 1].asDouble());
		finger_loc[8] = Point2f(root["people"][0U]["hand_right_keypoints_2d"][16 * 3].asDouble(), root["people"][0U]["hand_right_keypoints_2d"][16 * 3 + 1].asDouble());
		finger_loc[9] = Point2f(root["people"][0U]["hand_right_keypoints_2d"][20 * 3].asDouble(), root["people"][0U]["hand_right_keypoints_2d"][20 * 3 + 1].asDouble());
	}
	in.close();
	return finger_loc;
}

Mat transform()
{
	vector<Point2f> left_image;      
    vector<Point2f> right_image;

	Mat imageLogo(height,width, CV_8UC3, Scalar(0, 0, 0)); //矩阵行数列数、数据类型、CV_8UC后面的123表示通道数
    left_image.push_back(pts[0]);
    left_image.push_back(pts[1]);
    left_image.push_back(pts[2]);
    left_image.push_back(pts[3]);

    right_image.push_back(Point2f(float(0),float(0)));
    right_image.push_back(Point2f(float(imageLogo.cols),float(0)));
    right_image.push_back(Point2f(float(imageLogo.cols),float(imageLogo.rows)));
    right_image.push_back(Point2f(float(0),float(imageLogo.rows)));        

    Mat H = findHomography(left_image,right_image,0 );
    Mat logoWarped;
    warpPerspective(inputImage,logoWarped,H,imageLogo.size());
    Mat newimg = Mat(logoWarped, Rect(0, 0, imageLogo.cols, imageLogo.rows));  //(0,0)是矩形左上角的坐标,后两个是宽和高,就是调整图像大小
    //opencv绘制的图中零点坐标在左上角
    
    return newimg;
}

void solve(int,void*)
{
    float keyWidth = float(width)/keyNum;  //键宽
	int frametostop = 1860;
    while(capture.read(inputImage))    //逐帧读取视频帧
    {
		if (frames > frametostop)break;
		vector<int>whitekey;
		vector<vector<int> >blackkey;
		vector<int>black;
		resize(inputImage, inputImage, Size(1024, 576));  //改变图像大小

		Mat transformed = transform();
		Mat outputimg = transform();


		char buff[100];
		
        //背景检测法
		//neg_diff表示白键的，pos_diff表示黑键的，结果都要大于0
        Mat neg_diff = transformed - base, pos_diff = base - transformed;		
        Mat neg_diff1, pos_diff1;
        cvtColor(neg_diff,neg_diff1,CV_BGR2GRAY);  
        cvtColor(pos_diff,pos_diff1,CV_BGR2GRAY);

		char buf1[100],buf2[100],buf3[100];
		string save_path="/home/cy/openpose/piano/test_piano/image";
		sprintf(buf1,"%s/transformed_image/%dtrans.jpg",save_path.c_str(),frames);
		sprintf(buf2,"%s/neg_diff/%dneg.jpg",save_path.c_str(),frames);
		sprintf(buf3,"%s/pos_diff/%dpos.jpg",save_path.c_str(),frames);
		

		imwrite(buf1,transformed);
		imwrite(buf2,neg_diff1);
		imwrite(buf3,pos_diff1);


        for(int i=0;i<=keyNum;i++)
        {
			line(outputimg, Point2f(float(i*keyWidth), float(0)), Point2f(float(i*keyWidth), float(width)), Scalar(255), 1, 8);

        } 
        vector<int> pcount(keyNum+1,0),ncount(keyNum+1,0);
		
        //统计黑键和白键像素超过阈值的数量
		int blackStart = keyWidth / 2;   
		int blacknum;
		for (int i = 1; i <= keyNum; i++)
		{
			for (int row = 0; row < base.size().height; row++)
			{
				for (int col = 1; col<keyWidth-1; col++) 
				{
					if (pos_diff1.at<uchar>(row, (i - 1)*keyWidth + col) > value_threshold_w) pcount[i]++;
				}
			}
			for (int row = 0; row < base.size().height; row++){
				for (int col = 1; col < keyWidth-1; col++){    
					if (neg_diff1.at<uchar>(row, (i - 1)*keyWidth + col) > value_threshold_b) ncount[i]++;
				}
			}

			//白键按下
			if (pcount[i] > count_threshold_w)
			{
				whitekey.push_back(i);
				cv::rectangle(outputimg, Point((i - 1)*keyWidth+3, 0), Point(i*keyWidth-3, 40), Scalar(0, 255, 0), -1, 8, 0);
				cout << "Frame: " << frames << "  White key " << i << " pressed with val : " << pcount[i] << endl;
			}
			//黑键按下
			else if (ncount[i] > count_threshold_b)
			{
				cv::rectangle(outputimg, Point((i - 1)*keyWidth+3, 0), Point(i*keyWidth-3 , 20), Scalar(0, 0, 255), -1, 8, 0);
				//因为这里编号是按照白建的从1-52，这些判断语句是将相应的白建转换为黑键的编号
				if (i % 7 != 0 && i % 7 != 3){
					if (i % 7 < 3){
						blacknum = (i / 7) * 5 + (i % 7);
					}
					if (i % 7 > 3){
						blacknum = (i / 7) * 5 + (i % 7 - 1);
					}
					black.push_back(blacknum);
					//黑键被按下的坐标范围
					black.push_back((i - 1)*keyWidth+blackStart);
					black.push_back(i*keyWidth + blackStart);
					blackkey.push_back(black);
					black.clear();  //将black里面的内容清空
					cout << "Frame: " << frames << " Black key " << blacknum << " pressed with val : " << ncount[i] << endl;
				}
			}
		}
//---------------------pressed key correspond to finger-----------------------
		string videoname;
		int start = videopath.find_last_of("/");  
		int end = videopath.find_last_of(".");
		videoname = videopath.substr(start + 1, end - start-1); 
		string p="/home/cy/openpose/output/json_file";  
		sprintf(buff,"%s/%s_%012d_keypoints.json",p.c_str(),videoname.c_str(),frames);  
		string buf=buff;
		vector<Point2f>finger_loc=readJson(buf);    //读入Json文件，finger_loc存放的是手指弹的关键点位置
		ofstream file;
		//file.open("../record.txt",ios::out|ios::app);  
		
		if(whitekey.size()>0){
			string key = "white key";
			for(int i=0;i<whitekey.size();i++){
				//pts[0]存的是钢琴起始点,whitekey[]中存放的是被按下的白键
				int pressed_x_max = pts[0].x + whitekey[i] * keyWidth;
				int pressed_x_min = pts[0].x + (whitekey[i] - 1)*keyWidth;
				for (int j = 0; j < finger_loc.size(); j++){
					//手指坐标与被按下的键坐标是否吻合，是哪个手指按下了
					if (finger_loc[j].x >= pressed_x_min && finger_loc[j].x < pressed_x_max){
						switch (j)
						{
                        case 0:
							file << "frame: " << frames << " 左小指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 1:
							file << "frame: " << frames << " 左无名指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 2:
							file << "frame: " << frames << " 左中指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 3:
							file << "frame: " << frames << " 左食指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 4:
							file << "frame: " << frames << " 左大拇指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 5:
							file << "frame: " << frames << " 右大拇指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 6:
							file << "frame: " << frames << " 右食指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 7:
							file << "frame: " << frames << " 右中指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 8:
							file << "frame: " << frames << " 右无名指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 9:
							file << "frame: " << frames << " 右小指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						default:
							break;


						}
					}
				}
			}
		}
		if (blackkey.size() > 0){
			string key = "black key";
			for (int i = 0; i<blackkey.size(); i++){
				int pressed_x_max = pts[0].x + blackkey[i][2];
				int pressed_x_min = pts[0].x + blackkey[i][1];
				for (int j = 0; j < finger_loc.size(); j++){
					if (finger_loc[j].x >= pressed_x_min && finger_loc[j].x < pressed_x_max){
						//file << "frame: "<<frames<< "finger " << j << " press " << "Black key " << blackkey[i] << endl;
						switch (j)
						{
						case 0:
							file << "frame: " << frames << " 左小指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 1:
							file << "frame: " << frames << " 左无名指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 2:
							file << "frame: " << frames << " 左中指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 3:
							file << "frame: " << frames << " 左食指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 4:
							file << "frame: " << frames << " 左大拇指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 5:
							file << "frame: " << frames << " 右大拇指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 6:
							file << "frame: " << frames << " 右食指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 7:
							file << "frame: " << frames << " 右中指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 8:
							file << "frame: " << frames << " 右无名指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						case 9:
							file << "frame: " << frames << " 右小指 " << " press " << "White key " << whitekey[i] << endl;
							break;
						default:
							break;

						}
					}
				}
			}
		}	
		string output1 = "/home/cy/openpose/piano/test_piano/result";
		sprintf(buff, "%s/%d.jpg", output1.c_str(), frames);

		imwrite(buff, outputimg); 
        frames++;	

    }
}

int main()
{
    int frameToStart = 0;
	capture.set(CV_CAP_PROP_POS_FRAMES, frameToStart); 
	capture.read(inputImage);  
	//这里与openpose里的图片大小一样
    resize(inputImage, inputImage, Size(1024, 576));  

    ifstream myfile("/home/cy/openpose/piano/Music-Transcription/build/prev_pts.txt");
    if (myfile.is_open())
    {
        string line;
        while (getline(myfile, line))
        {
            istringstream iss(line);
            int x, y, z;
            iss >> x;
            iss >> y;
            iss >> z;
            pts.push_back(Point(x, y));

        }
        myfile.close();
    }
	int n = 0;

    Mat mask = Mat::zeros(inputImage.size(), CV_8UC1);  //灰度图像
    //mask是空的矩阵，灰度图，在这里只需要得到钢琴键盘的框框就可以了
	for(int i = 0; i < 4; ++i)
    {
    	line( mask, pts[i], pts[(i+1)%4], Scalar(255), 2, CV_AA);  //起始的4个坐标
    }
    vector<vector<Point> > contours;
	vector<Vec4i> hierarchy;  //<Vec4i>表示Hierarchy存放的是4维int向量（每个元素包含了4个Int型变量）
    findContours(mask, contours, hierarchy, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );	
    RotatedRect minRect = minAreaRect(Mat(contours[0]));  //求包含点集（数据在contours[]中）最小面积的矩形

    Point2f rect_points[4];   
	minRect.points( rect_points );  

	//矩形的宽和高
  	float l = dist(rect_points[0], rect_points[1]), b = dist(rect_points[2], rect_points[1]);
  	width = max(l, b);   //只包含钢琴矩形框的宽和高
  	height = min(l, b);
    base = transform();
	imwrite("/home/cy/openpose/piano/test_piano/image/1.jpg",base);

	solve(0, 0);
	return 0;
}