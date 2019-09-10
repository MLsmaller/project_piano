#include<iostream>
#include<vector>
#include<dirent.h>
#include<opencv2/opencv.hpp>
#include<get_keyboard.hpp>
#include<utils.hpp>
#include<detect_key.hpp>
#include<string>
using namespace std;
using namespace cv;

string video_path = "/home/lj/cy/openpose/some_code/video_to_image/test2.mp4";
string videoSavepath="/home/lj/cy/openpose/piano/test_piano/image/temp_dir/";
string cropSavepath="/home/lj/cy/openpose/piano/test_piano/image/temp_crop/"; 

string white_path = "/home/lj/cy/openpose/piano/test_piano/new_res/w_key/";

int main(){
    //将视频转换为帧
    int frameTostop = 600;
    bool flags = false;
    video_to_frame(video_path,videoSavepath,frameTostop,flags);

    Mat src,src_rgb, src_rgb1,base;
    string img_extern = "/home/lj/cy/openpose/piano/test_piano/image/temp_dir/*.jpg";  //以jpg结尾的图片
    vector<string> fn;  
    glob(img_extern, fn, false);  //fn中存着图片的路径
    //首先找到一张能够检测到钢琴的帧(有些视频开头不包含钢琴),但是可能亮度不高
    vector<int> begin_num;
    //ratio为图像经过canny边缘检测之后得到图片的白色像素占图片总像素的比例(一般有钢琴的图那块区域会有白色像素)
    float thr_ratio = 0.005;
    vector<Rect>box_keyboard;
    int frames = 0;
    for (int i = 270; i < fn.size();i++){
        base = imread(fn[i]);
        float ratio;
        //得到钢琴键盘图片
        vector<Vec4i> lines;
        base = keyboard(base,box_keyboard,ratio,lines);
        if((ratio>thr_ratio)&&(lines.size()>1)){
            begin_num.push_back(i);
            cout << "首次检测到钢琴的图片为: "<<fn[i] << endl;
            imwrite("../base.jpg", base);
            break;
        } 
/*         if(base.empty()){
            cout << "当前帧未检测到钢琴" << endl;
            cout << fn[i] << endl;
        }
        else{
            cout << fn[i] << endl;
            break;
        }     */    
    }
    
    Rect box = box_keyboard.back();
    cout << box << endl;
    bool isCrop = false;   //是否需要进行裁剪
    //重新裁剪
    if (isCrop){
        for (int i = 0; i < fn.size();i++){
            Mat img1 = imread(fn[i]);
            Mat crop_img = Mat(img1, box);
            char buf_crop[80];
            sprintf(buf_crop, "%s%04d.jpg", cropSavepath.c_str(), i);
            //cout << buf_crop << endl;
            imwrite(buf_crop, crop_img);
        }
    }
    //按照第一次检测到钢琴图片的框进行图片裁剪(只包含钢琴)
    vector<string> fn_crop;  //也可以不存入路径,直接裁剪后进行后面的步骤
    string crop_path = cropSavepath + "*.jpg";
    glob(crop_path, fn_crop, false);
    //检测最适合作为背景图的图片下标索引
    int base_index = begin_num[0];
    base_index=find_base(base, begin_num[0], fn_crop,base_index);
    cout << "背景图片下标索引为: " << base_index << endl;

    Mat base_img;          //背景图
    base_img = imread(fn_crop[base_index]);
    cout << "背景图片是  " << fn_crop[base_index] << endl;
    cout << base_img.size() << endl;
    Mat base_img_rgb(base_img);
    Mat test_img(base_img);
    imwrite("../keyboard.jpg", base_img);
	cvtColor(base_img,base_img,CV_BGR2GRAY);
    int b_height = base_img.rows;  //base_img.rows
    int b_width=base_img.cols;     
	vector<Rect>black_box;
	vector<double>white_loc;
	vector<double>ori_white_loc;
	vector<int>area;
    //------得到黑键和白键的坐标位置------- 
	key_loc(base_img,black_box,white_loc,area);
	for(vector<double>::iterator iter=white_loc.begin();iter<white_loc.end();iter++){
		ori_white_loc.push_back(*iter+double(box.tl().x));
	}

/*     vector<double> x_loc;
    vector<int> w_nums;
    vector<int> b_nums;
    for (int i = 0; i < white_loc.size();i++){
        x_loc.push_back(white_loc[i]);
    }
    for (int i = 0; i < black_box.size();i++){
        //cout << black_box[i].tl().x << endl;
        x_loc.push_back(black_box[i].tl().x);

    }
    sort(x_loc.begin(), x_loc.end(), less<double>());
    for (int i = 0; i < x_loc.size();i++){
        string index = to_string(i+1);
        vector<double>::iterator it;
        it=find(white_loc.begin(),white_loc.end(),x_loc[i]);
        if(it==white_loc.end()){
            putText(test_img, index, Point2f(x_loc[i], 2.0 / 3 * b_height), FONT_HERSHEY_COMPLEX, 0.6, Scalar(0, 0, 255), 1);
            b_nums.push_back(i + 1);
        }
        else{
            putText(test_img, index, Point2f(x_loc[i], 2.0 / 3 * b_height+15), FONT_HERSHEY_COMPLEX, 0.5, Scalar(255, 0, 0), 1);
            w_nums.push_back(i + 1);
        }
        //line(base_img,Point2f(x_loc[i],0),Point2f(x_loc[i],b_height),Scalar(0,0,255),1,CV_AA);
        
    }


    imwrite("../draw_keys.jpg", test_img); */

    //-----找到白键所在的那个框框,就是最后按键出来的效果-------
    vector<Rect> total_top;
    vector<Rect> total_bottom;
    find_box(base_img_rgb, white_loc, black_box, total_top, total_bottom);
 

              
        /*     //从背景图片后一帧开始检测是否有按键(也可以从最开始的图片开始进行检测)
	for(size_t num=base_index+1;num<fn_crop.size();num++){     
		string img_name=fn_crop[num];
        char img_path[80];
		sprintf(img_path,"%s%s",save_path.c_str(),img_name.c_str());
		src_rgb = imread(img_path);   
		if (src_rgb.empty())
			exit(-1);
		Mat current_frame=src_rgb.clone();
		cvtColor(current_frame,current_frame,CV_BGR2GRAY);
		int stepsize=30;
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

		vector<int>pixel_num_w;
//---------检测哪个白键被按下--------
		float ratio=0.1;     //白色像素面积占比大于该区域总面积0.1则认为按下
		left_hand=left_point[num];
		cout<<"坐标图片为 "<<file_name[num]<<endl;
		right_hand=right_point[num];
		if ((left_hand.size()==1)&&(right_hand.size()==1)){    //如果没有手其坐标存入的是[]
			cout<<"当前帧没有白键被按下 (没检测到手)"<<endl;
		}

		char buf_w[80];
		sprintf(buf_w,"%swhite_%04d.jpg",white_path.c_str(),frames);
		cout << buf_w << endl;

		vector<int> pre_w;
		pre_w=detect_w(src_rgb, white, left_hand, white_loc, black_box, box, ratio, pre_w);
		pre_w=detect_w(src_rgb, white, right_hand, white_loc, black_box, box, ratio,pre_w);
		sort(pre_w.begin(), pre_w.end());  //对按下的键进行升序排序 */

        return 0;
}
