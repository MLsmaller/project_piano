#include<opencv2/opencv.hpp>
#include<json/json.h>
#include<iostream>
#include<fstream>
#include<vector>
using namespace cv;
using namespace std;


void get_keypoint(const string &json_name,vector<vector<Point>>&left_point,vector<vector<Point>>&right_point,vector<string>&img_name){
    Json::Reader reader;
    Json::Value root;
    ifstream in;
    in.open(json_name.c_str(), ios::binary);
    if(!in.is_open()){
        cout<<"Error open json file\n";
    }

    if(reader.parse(in,root)){
        Json::Value data=root["value"];
        int size=data.size();
        string filename;
        //逐张读取存储了在Json文件中包含关键点信息的图片
        for(int i=0;i<size;i++){
            filename =data[i]["filename"].asString();
            img_name.push_back(filename);
            Json::Value point_l=data[i]["keypoint_l"];   //Json文件直接用索引取某个值要加个U,用for循环时又不用
            Json::Value point_r=data[i]["keypoint_r"];
            int length_l=point_l.size();
            int length_r=point_r.size();
            vector<Point>hand_l;
            vector<Point>hand_r;
            if (length_l>0){
                for(int i=0;i<length_l;i++){
                    //分别取出当前帧21个关键点的坐标，如果某个关键点没检测到，则存入(0,0)
                    if(point_l[i].size()==0){
                        hand_l.push_back(Point(0,0));
                    }
                    else{
                        hand_l.push_back(Point(point_l[i][0U].asInt(),point_l[i][1U].asInt()));
                    }  
                }
            }
            else{
                hand_l.push_back(Point(0,0));
            }
            if (length_r>0){
                for(int i=0;i<length_r;i++){
                    if(point_r[i].size()==0){
                        hand_r.push_back(Point(0,0));
                    }
                    else{
                        hand_r.push_back(Point(point_r[i][0U].asInt(),point_r[i][1U].asInt()));
                    }  
                }
            }
            else{
                hand_r.push_back(Point(0,0));
            }
            left_point.push_back(hand_l);
            right_point.push_back(hand_r);
        } 
    }

}

//----背景减除法,得到当前帧和背景帧不同的像素点
Mat background_subtract(Mat &base,Mat &img_keyboard,const int &threshold,Mat &black){	
    int b_width=base.cols;
    int b_height=base.rows;
    //black1=black.clone();
	Mat white=black.clone();              //detect whitekey
    for(int i=0;i<b_width;i++)
    {
        uchar *data1=base.ptr<uchar>(i);
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
    return white;
}

void video_to_frame(const string &video_path, const string &save_path, const int &frameTostop,bool conver)
{
    if(conver){
        VideoCapture cap (video_path);
        if(!cap.isOpened()){
            cout<<"the video fail to open"<<endl;  //视频被成功打开返回true
        }
        //获取视频总帧数
        long totalFrameNumber = cap.get(CV_CAP_PROP_FRAME_COUNT);  //long占用8个字节
        cout<<"total frames of video is : " << totalFrameNumber << endl;

        Mat frame;
        bool flags = true;
        long currentFrame = 0;
        vector<Rect>loc;
        //loc.push_back(Rect(20,476,1237,148));
        while(flags){
            //读取视频每一帧
            cap.read(frame);  //获取，解码
    /*         //stringstream类对象可以和cout一样使用,通过运算符<<将数据传递给stringstrream对象
            //之后再通过stringstream类的函数str()将对象所包含的内容赋值给一个string对象,可以用于存储路径
            stringstream str;
            str<<"pic"<<currentFrame<<".jpg";
            cout<<"正在处理第"<<currentFrame<<"帧"<<endl;
            cout<<endl; */
            char buf[100];
            sprintf(buf,"%s%04d.jpg",save_path.c_str(),currentFrame);
            cout<<buf<<endl;
            imwrite(buf, frame);
            /*             if(currentFrame>300){
                //Mat frame1=Mat(frame,loc[0]);
                //imwrite(buf,frame1);
                imwrite(buf,frame);
            } */

            /*
            //设置每30帧获取一帧
            if(currentFrame%25==0){
                //将帧转换为图片输出
                imwrite("/home/cy/openpose/some_code/video_to_image/res/" + str.str(),frame);
            }
            */
            //结束条件
            currentFrame++;
            if(currentFrame>=totalFrameNumber){
                flags = false;
            }
            
        }
    } 
}