#include<iostream>
#include<fstream>
#include<vector>
#include<string>
#include <sstream>
#include<cmath>
#include<dirent.h>
#include<json/json.h>
#include<opencv2/opencv.hpp>
#include<get_keyboard.hpp>
#include<bwlabel.hpp>
#include<utils.hpp>
#include<detect_key.hpp>
#include<to_json.hpp>

using namespace std;
using namespace cv;

string cropSavepath="/home/data/cy/projects/piano/KJnotes/frames2/crop_img/"; 
string pressed_white="/home/data/cy/projects/piano/KJnotes/frames2/res_img/";
string num_oriImg="/home/data/cy/projects/piano/KJnotes/frames2/num_oriImg/";

int main(){

    Mat src,src_rgb, src_rgb1,base;
    string img_extern = "/home/data/cy/projects/piano/KJnotes/frames2/whole_img/*.jpg";  //以jpg结尾的图片,视频原始图片
    vector<cv::String> fn;  //调用glob函数时其fn类型是cv:String类
    glob(img_extern, fn);  
    vector<int> begin_num;
    //-----这里用于测试,背景图直接用选好的那张0608.jpg
    Rect box;
    box = Rect(32, 499, 1260, 639);  //  钢琴键盘的box

    vector<cv::String> fn_crop;  //也可以不存入路径,直接裁剪后进行后面的步骤
    string crop_path = cropSavepath + "*.jpg";
    glob(crop_path, fn_crop);

    int base_index = 0;
    Mat base_img;
    base_img = imread("/home/data/cy/projects/piano/KJnotes/frames2/crop_img/0608.jpg");
    imwrite("../base_img.jpg", base_img);
    cout << "背景图片大小为 "<< base_img.size() << endl;

    Mat base_img_rgb(base_img);
	cvtColor(base_img,base_img,CV_BGR2GRAY);
    int b_height = base_img.rows;  //base_img.rows
    int b_width = base_img.cols;
    vector<Rect>black_box;
	vector<double>white_loc;
	vector<double>ori_white_loc;
	vector<int>area;
    //------得到黑键和白键的坐标位置------- 
	key_loc(base_img,black_box,white_loc,area);


    //-----找到白键所在的那个框框,就是最后按键出来的效果-------
    vector<Rect> total_top;
    vector<Rect> total_bottom;
    find_box(base_img_rgb, white_loc, black_box, total_top, total_bottom);

    //-----------get the keypoing of hand--------
    string json_name="/home/data/cy/projects/piano/KJnotes/json_dir/hand_keypoint2.json";
	vector<vector<Point> >left_point;
	vector<vector<Point> >right_point;
	vector<Point>left_hand;
	vector<Point>right_hand;
	vector<string>file_name;
	get_keypoint(json_name,left_point,right_point,file_name);

    //-------与背景图相减检测按键-----
    int frames = 0;
    int begin_index = 0;
    int Tostop = 1000;
    Json::Value root;
    for(size_t num=begin_index;num<fn_crop.size();num++){

        string img_name=fn_crop[num];
        cout<<"当前帧为: "<<fn_crop[num]<<endl;
        cout<<"\n"<<endl;
        src_rgb = imread(img_name);
        if (src_rgb.empty())
			exit(-1);
		Mat current_frame=src_rgb.clone();
		cvtColor(current_frame,current_frame,CV_BGR2GRAY);
		int stepsize=20;
		//--------------光照归一化---------------
		illumination(current_frame,base_img,stepsize);
		Mat black(b_height,b_width,CV_8UC1);    //detect blackkey. 
		Mat white=black.clone();                //detect whitekey

//根据当前帧与背景帧每个像素点的差值是否大于阈值来判断是否有差异
//大于阈值的地方像素点为255,分别得到检测黑键和白键的两张灰度图 
		int threshold=25;
		for(int i=0;i<b_height;i++)  //遍历时是rows×cols,相当于height×width
		{
			uchar *data1=base_img.ptr<uchar>(i);
			uchar *data2=current_frame.ptr<uchar>(i);
			uchar *data3=black.ptr<uchar>(i);
			uchar *data4=white.ptr<uchar>(i);
			for(int j=0;j<b_width;j++)     
			{	
				if((data2[j]-data1[j])>threshold){   //detect blackkey
					data3[j]=255;
				}
				else{
					data3[j]=0;
				}
				if((data1[j]-data2[j])>threshold){    //detect whitekey
					data4[j]=255;
				}
				else{
					data4[j]=0;
				}
			}
		}

//---------检测哪个白键被按下--------
		float ratio=0.03;     //白色像素面积占比大于该区域总面积0.1则认为按下
		left_hand=left_point[num];
		right_hand=right_point[num];

		if ((left_hand.size()==1)&&(right_hand.size()==1)){
			cout<<"当前帧没有白键被按下 (没检测到手)"<<endl;
		}
        vector<int> pre_w1;
        vector<int> pre_w2;
        vector<int> pre_w;

        Mat test_img=src_rgb.clone();
        for (int i = 0; i < white_loc.size()-1; i++)
        {
            string text_num = std::to_string(i + 1);
            putText(test_img, text_num, Point(white_loc[i], 15), FONT_HERSHEY_COMPLEX, 0.5, Scalar(0, 0, 255), 2);
        }
        char buf_num[80];
		sprintf(buf_num,"%s%04d.jpg",num_oriImg.c_str(),frames);
		//cout << "标有数字的图片路径为: "<<buf_num << endl;
        imwrite(buf_num, test_img);


        pre_w1=detect_w1(src_rgb, white, left_hand, white_loc, black_box,
                        box, ratio, pre_w1,total_top,total_bottom);
		pre_w2=detect_w1(src_rgb, white, right_hand, white_loc, black_box,
                        box, ratio,pre_w2,total_top,total_bottom);
		
        for (int i = 0; i < pre_w1.size();i++){
            pre_w.push_back(pre_w1[i]);
        }
        for (int i = 0; i < pre_w2.size();i++){
            pre_w.push_back(pre_w2[i]);
        }
        sort(pre_w.begin(), pre_w.end());  //对按下的键进行升序排序
        for (int i = 0; i < pre_w.size();i++){
            cout << "当前帧检测到的按键有: " << pre_w[i] << endl;
        }

        //----标一下白键的序号------
        vector<int> cy = {0, 0, 1, 2, 2};
        for (int i = 0; i < white_loc.size()-1; i++)
        {
            string text = std::to_string(i + 1);
            putText(src_rgb, text, Point(white_loc[i], 15), FONT_HERSHEY_COMPLEX, 0.5, Scalar(0, 0, 255), 2);
        }
        char buf_w[80];
		sprintf(buf_w,"%s%04d.jpg",pressed_white.c_str(),frames);
		//cout << "标有数字的图片路径为: "<<buf_w << endl;
        imwrite(buf_w, src_rgb);

		Json::Value partner;
		partner = to_json(buf_w, pre_w);
		//根节点与子节点的转换
		char id[20];
		sprintf(id, "%04d", frames);  
		string index(id);     
		root[index] = Json::Value(partner);

        char buf1[80];
        char buf2[80];
        string black_path = "/home/data/cy/projects/piano/KJnotes/frames2/dif_res/b_detect/";
        string white_path = "/home/data/cy/projects/piano/KJnotes/frames2/dif_res/w_detect/";
        sprintf(buf1,"%s%04d_neg.jpg",black_path.c_str(),frames);
        imwrite(buf1,black);
        sprintf(buf2,"%s%04d_pos.jpg",white_path.c_str(),frames);
        imwrite(buf2,white); 
        frames++;
        if(frames>Tostop){  //不用时Tostop设大一点就好
            break;
        } 
    }

	char buf21[80];
	string pro_path = "/home/data/cy/projects/piano/KJnotes/json_dir/";
	string fileName = "pressed_w2.json";    //---生成的按键的json文件----
	sprintf(buf21, "%s%s", pro_path.c_str(),fileName.c_str());
	Json::StyledWriter fw;  //这是缩进输出,FastWriter是直接输出
	ofstream fout;   //类似于cout
    fout.open(buf21);
    assert(fout.is_open());
	fout << fw.write(root);
	fout.close();
    cout << "the pressed_w.json has done " << endl; 
    return 0;
}
