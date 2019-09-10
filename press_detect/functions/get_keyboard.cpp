#include<opencv2/opencv.hpp>
#include<get_keyboard.hpp>
#include "bwlabel.hpp"
#include<string>
#include<vector>
#include<iostream>
#include<iterator>
//#include<numeric>   //调用accumulate()函数对vcctor进行求和
using namespace std;
using namespace cv;

//------去除钢琴中一部分上面和下面的部分,以便于检测黑键的位置(灰度图片)
Mat remove_region(Mat &result)
{
	//如果是RGB图片,还要考虑通道channel,遍历图片的方式则不同
	int width = result.cols;
	int height = result.rows;

	for (int i = 0; i < 0.05*height; i++) {
		uchar *data = result.ptr<uchar>(i);
		for (int j = 0; j < width; j++) {
			data[j] = 255;        //变为白色像素
		}
	}
	for (int i = 0; i < height; i++) {
		uchar *data = result.ptr<uchar>(i);
		for (int j = 0; j < width; j++) {
/* 			if(i > 0.95*height){
				data[j] = 255;
			} */
			if ((i > (2.0/3)*height) || (j < 0.004*width) || (j > 0.992*width))
			{
				data[j] = 255;
			}
		}
	}
	return result;
}

//------得到黑键和白键的坐标位置
void key_loc(const Mat &img,vector<Rect> &black_box,vector<double> &white_loc,vector<int> &area){
	Mat base=img.clone();
	int width=img.cols;
	int height=img.rows;
	Mat img_ori=img.clone();
	base=remove_region(base);
	threshold(base, base,120, 255, THRESH_BINARY);  //可以使用Osty thresholding method?
	//不同的钢琴视频可能光照强度不一样,因此阈值会有不同
	//-----用region label来定位出钢琴可以试一下-----
	imwrite("../region.jpg", base);
	GaussianBlur(base, base, Size(5, 5), 2);
	Mat dst;
	vector<Feather>featherlist;
	int num = bwlabel(base, dst, featherlist);
	cout << num << endl;
	vector<Point>black_loc;
	int frames = 0;
	for (vector<Feather>::iterator iter = featherlist.begin(); iter < featherlist.end(); iter++)
	{
		if(iter->area>300){   //---因为有些光照不是特别清楚,导致某个黑键下面会有一些白色像素导致检测多了区域(这种区域面积一般很小)
			area.push_back(iter->area);
			//cout << "面积大小为: " << iter->area << endl;
			//rectangle(img_ori, iter->boundinbox, Scalar(0, 255, 0));
			string text = std::to_string(frames);
			// putText(img_ori, text, Point(int(iter->boundinbox.tl().x), int(iter->boundinbox.tl().y+20)), FONT_HERSHEY_COMPLEX, 0.5,Scalar(0, 255, 0), 1);
			//putText(img, index, Point2f(x_loc[i], 2.0 / 3 * b_height+15), FONT_HERSHEY_COMPLEX, 0.5, Scalar(255, 0, 0), 1);
			frames++;
			black_box.push_back(iter->boundinbox);
			black_loc.push_back(iter->boundinbox.tl());  //.tl()是Rect类的成员函数
			//存储着每个黑键的左上角坐标
		}

	}
	// imwrite("../rect.jpg", img_ori);
	for (int i = 0; i < area.size(); i++)
	{	
		cout << "第 " << i << " 个矩形框的面积为: ";
		cout << area[i] << endl;;
	} 

	//钢琴除掉前面的两个白键和一个黑键以及最后一个黑键,其它可以有规律的分为7个区域
	//由于角度等原因对每个区域计算白键间隔都不同
	//这些23、41等数值是参考网页中the size of the piano keyboard得出的
	int black_gap1=black_loc[3].x-black_loc[2].x; 
	double WhiteKey_width1=(23.0/41)*(black_gap1);  //根据白键所占的比例计算出白键间隔
	//由于第四个黑键是被均分两半的，因此从这里开始计算每个区域的起始位置
	int half_width1=black_box[4].width;
	//第一个区域的起始位置坐标
	double keybegin=black_loc[4].x+double(half_width1/2.0)-7.0*WhiteKey_width1;  //第一次减多两个
	//double whitebegin=keybegin+WhiteKey_width1*2;
	int whitekey_num=52;
	int blackkey_num=36;
	for(int i=0;i<10;i++){    //第一次黑键循环(要包括第一个黑键)
		line(img_ori,Point2f(keybegin+i*WhiteKey_width1,0),Point2f(keybegin+i*WhiteKey_width1,height),Scalar(0,0,255),1,CV_AA);
		white_loc.push_back(keybegin+i*WhiteKey_width1);
	}
	for(int i=0;i<6;i++){     //剩下黑键还有6次循环
		int axis=8+i*5;
		int black_gap2=black_loc[axis].x-black_loc[axis-1].x;
		double WhiteKey_width2=(23.0/41)*(black_gap2);
		int half_width2=black_box[axis+1].width;
		double keybegin1=black_loc[axis+1].x+double(half_width2/2.0)-5.0*WhiteKey_width2;
		for(int i=1;i<8;i++){
			line(img_ori,Point2f(keybegin1+i*WhiteKey_width2,0),Point2f(keybegin1+i*WhiteKey_width2,height),Scalar(0,0,255),1,CV_AA);
			white_loc.push_back(keybegin1+i*WhiteKey_width2);
		}
		if(i==5){   //最后一次循环时把钢琴最后一个白建加进去
			//判断是否超过图片右边界
			if(width<int(keybegin1+8*WhiteKey_width2)){
				white_loc.push_back(width-1);
			}
			else{
				white_loc.push_back(keybegin1+8*WhiteKey_width2);
			}
			//.back()函数取vector<>中的最后一个元素
			line(img_ori,Point2f(white_loc.back(),0),Point2f(white_loc.back(),height),Scalar(0,0,255),1,CV_AA);
		}
	}
	cout<<"the number of whitekey_num is "<<white_loc.size()<<endl;
	imwrite("../key_ling.jpg",img_ori);
}

//------将黑键和白键的序号都标出来,不区分黑白键,总共88个按键------
/* void draw_whole_keys(const Mat& img,const vector<double>&white_loc,const vector<Rect>black_box,const int&b_height){
    vector<double> x_loc;
    for (int i = 0; i < white_loc.size();i++){
        x_loc.push_back(white_loc[i]);
    }
    for (int i = 0; i < black_box.size();i++){
        //cout << black_box[i].tl().x << endl;
        x_loc.push_back(black_box[i].tl().x);

    }
	//对横坐标进行排序
    sort(x_loc.begin(), x_loc.end(), less<double>());

    for (int i = 0; i < x_loc.size();i++){
        string index = to_string(i+1);
        vector<double>::iterator it;
		//如果该坐标为白键的坐标,则画的位置靠近下面一点-
        it=std::find(white_loc.begin(),white_loc.end(),x_loc[i]);
        if(it==white_loc.end()){
            putText(img, index, Point2f(x_loc[i], 2.0 / 3 * b_height), FONT_HERSHEY_COMPLEX, 0.6, Scalar(0, 0, 255), 1);
        }
        else{
            putText(img, index, Point2f(x_loc[i], 2.0 / 3 * b_height+15), FONT_HERSHEY_COMPLEX, 0.5, Scalar(255, 0, 0), 1);
        }
        //line(base_img,Point2f(x_loc[i],0),Point2f(x_loc[i],b_height),Scalar(0,0,255),1,CV_AA);
        
    }
    imwrite("../draw_keys.jpg", img);

} */