#include<string>
#include<iostream>
#include<fstream>
#include<vector>
#include<numeric>
#include<cmath>
#include<json/json.h>
#include<opencv2/opencv.hpp>
#include<bwlabel.hpp>
#include<get_keyboard.hpp>
#include<utils.hpp>
#include<detect_key.hpp>
#include<to_json.hpp>
using namespace std;
using namespace cv;


string save_path = "/home/lj/cy/openpose/some_code/video_to_image/res/test2/";
Directory dir;     
string extent=".jpg";
vector<string> FileLists = dir.GetListFiles(save_path, ".jpg", false); //true则返回的为绝对路径,false为文件名
char img_path[80];
string test_path = "/home/lj/cy/openpose/piano/test_piano/res/test_background/";
int frames=0;
string black_path = "/home/lj/cy/openpose/piano/test_piano/res/line_black/";
string white_path = "/home/lj/cy/openpose/piano/test_piano/res/line_white/";
string white_path1 = "/home/lj/cy/openpose/piano/test_piano/res/video/white/";
char buf_save[80];
int main(int argc, char *argv[])
{
	Mat src,src_rgb;
	int begin_num=300;
	Mat base=imread(save_path+FileLists[begin_num]);
	cout<<"the name of base img is "<<save_path+FileLists[begin_num]<<endl;
	//Mat img_ori=base.clone();
	cvtColor(base,base,CV_BGR2GRAY);
	int b_height=base.size().height;
	int b_width=base.size().width;
	vector<Rect>black_box;
	vector<double>white_loc;
	vector<double>ori_white_loc;
	vector<int>area; 
	Mat baseTotest=base.clone();
	//imwrite("./1.jpg", baseTotest);
	//------得到黑键和白键的坐标位置
	key_loc(baseTotest,black_box,white_loc,area);
	Rect box=Rect(20,476,1237,148);
	//------将黑键和白键位置转换到原始坐标中
	for(vector<double>::iterator iter=white_loc.begin();iter<white_loc.end();iter++){
		ori_white_loc.push_back(*iter+double(box.tl().x));
	}
	string json_name="/home/lj/projects/detection/detectHand/sfd_hand/hand_point.json";
	//----get the keypoing of hand
	vector<vector<Point>>left_point;
	vector<vector<Point>>right_point;
	vector<Point>left_hand;
	vector<Point>right_hand;

	vector<string>file_name;
	get_keypoint(json_name,left_point,right_point,file_name);

	
	int axis=0;
	int test_num=500;   //一个起始帧的编号，随便设置,因为该视频前面有很多帧都不包含手
	int c_num=test_num+600;
	vector<int> press_key_w;
	Json::Value root;
	//for(size_t num=c_num+150;num<c_num+161;num++){
	for(size_t num=test_num;num<test_num+700;num++){     
		string img_name=FileLists[num];
		//cout<<"the img is "<<img_name<<endl;
		//if (img_name=="0815.jpg"){

		sprintf(img_path,"%s%s",save_path.c_str(),img_name.c_str());
		src_rgb = imread(img_path);   
		if (src_rgb.empty())
			exit(-1);
		Mat img_keyboard=src_rgb.clone();
		cvtColor(img_keyboard,img_keyboard,CV_BGR2GRAY);
		int stepsize=30;
		//光照归一化，使得当前帧图片与背景帧图片除掉手指的区域外较为相似,以便后面的检测
		illumination(img_keyboard,base,stepsize);
		//imwrite("../illumi.jpg",img_keyboard);
		//imwrite("../illumi_1.jpg",base);
		Mat black(b_height,b_width,CV_8UC1);   //detect blackkey.
		//Mat创建时写height×width 
		Mat white=black.clone();              //detect whitekey

//根据当前帧与背景帧每个像素点的差值是否大于阈值来判断是否有差异
//大于阈值的地方像素点为255,分别得到检测黑键和白键的两张灰度图 
		int threshold=25; 
		for(int i=0;i<b_height;i++)  //遍历时是rows×cols,相当于height×width
		{
			uchar *data1=base.ptr<uchar>(i);
			uchar *data2=img_keyboard.ptr<uchar>(i);
			uchar *data3=black.ptr<uchar>(i);
			uchar *data4=white.ptr<uchar>(i);
			for(int j=0;j<b_width;j++)     
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
/*		
//---------统计每个黑键中的白色像素--------
		vector<int>pixel_num_b;
		for(vector<Rect>::iterator iter=black_box.begin();iter<black_box.end();iter++){
			int box_x=(*iter).tl().x;
			//int box_y=(*iter).tl().y;
			int box_width=(*iter).width;
			int box_height=(*iter).height;
			int b_count=0;
			for(int i=0;i<b_height;i++){
				uchar *data_b=black.ptr<uchar>(i);
				for(int j=0;j<b_width;j++){
					if((j>box_x)&&(j<(box_x+box_width))&&(i<box_height)){
						if(int(data_b[j])==255){
							b_count++;
						}
					}
				}	
			}
			pixel_num_b.push_back(b_count);
		}
		
//---------检测哪个黑键被按下--------		
		for(int i=0;i<pixel_num_b.size();i++){
			int area_b=area[i];
			int pixel=pixel_num_b[i];
			if((pixel>0.1*area_b)&&(pixel<0.5*area_b)){
				cout<<"第 "<<i<<"个黑键被按下"<<endl;  //加上手的坐标是否在这里一起判断
				Rect line_box=Rect(black_box[i].tl().x,0,black_box[i].width,int(0.5*black_box[i].height));
				rectangle(src_rgb,line_box,Scalar(0,0,255),-1);
				sprintf(buf_save,"%sblack_%04d.jpg",black_path.c_str(),frames);
				imwrite(buf_save,src_rgb);
				cout<<"the pressed img is "<<buf_save<<endl;
			}
			else{
				sprintf(buf_save,"%sblack_%04d.jpg",black_path.c_str(),frames);
				imwrite(buf_save,src_rgb);
			}
			//cout<<pixel_num_b[i]<<endl;
		}
*/
//d
//---------统计每个白键中的白色像素--------
		vector<int>pixel_num_w;
		vector<double>white_loc1(white_loc);   //拷贝一份white_loc在开头插入0以便后面统计像素
		white_loc1.insert(white_loc1.begin(),0.0);

//---------检测哪个白键被按下--------
		float ratio=0.1;     //白色像素面积占比大于该区域总面积0.1则认为按下
		left_hand=left_point[num-300];
		cout<<"坐标图片为 "<<file_name[num-300]<<endl;
		right_hand=right_point[num-300];
		if ((left_hand.size()==1)&&(right_hand.size()==1)){
			cout<<"当前帧没有白键被按下 (没检测到手)"<<endl;
		}

		char buf_w[80];
		sprintf(buf_w,"%swhite_%04d.jpg",white_path1.c_str(),frames);
		cout << buf_w << endl;

		vector<int> pre_w;
		pre_w=detect_w(src_rgb, white, left_hand, white_loc, box, ratio, pre_w);
		pre_w=detect_w(src_rgb, white, right_hand, white_loc, box, ratio,pre_w);
		sort(pre_w.begin(), pre_w.end());  //对按下的键进行升序排序
		
		Json::Value partner;
		partner = to_json(buf_w, pre_w);
		//根节点与子节点的转换
		char id[20];
		sprintf(id, "%04d", frames);  //都弄成4位数,这样存入json的时候才能顺序进行存取,0123...
		string index(id);      //将char类型转换为string类型,直接在定义的时候转换
		root[index] = Json::Value(partner);

		for (int i = 0; i < white_loc.size();i++){
			string text = to_string(i+1);  //to_string函数将int转换为string类型
			double font_scale = 0.5;
			putText(src_rgb, text, Point(white_loc[i + 1] - 20, 20), FONT_HERSHEY_COMPLEX, font_scale, Scalar(0, 0, 255), 2);
		//text为string类型,Point为文字左下角坐标,font_scale为字体大小
		}

		imwrite(buf_w, src_rgb);


		for(int i=0;i<pixel_num_w.size();i++){
			int pixel_w=pixel_num_w[i];
			//cout<<pixel_num_w[i]<<endl;
		}
		

		//left_tip.clear();
/* 		left_hand=left_point[axis];

		cout<<typeid(left_hand[0].x).name()<<endl; */   


		char buf1[80];
		char buf2[80];
		sprintf(buf1,"%sneg_%04d.jpg",test_path.c_str(),frames);
		imwrite(buf1,black);
		sprintf(buf2,"%spos_%04d.jpg",test_path.c_str(),frames);
		imwrite(buf2,white);  
		frames++;
		axis++;
		

	}

	char buf21[80];
	string pro_path = "/home/data/cy/projects/piano/";
	string fileName = "pressed_w.json";
	sprintf(buf21, "%s%s", pro_path.c_str(),fileName.c_str());
	Json::StyledWriter fw;  //这是缩进输出,FastWriter是直接输出
	ofstream fout;   //类似于cout
    fout.open(buf21);
    assert(fout.is_open());
	fout << fw.write(root);
	fout.close();
	string realTxtFile = "/home/lj/cy/openpose/piano/test_piano/res/new_data.txt";
	
	return 0;
}




