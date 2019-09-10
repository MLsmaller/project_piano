#ifndef _BWLABEL_H_
#define _BWLABEL_H
#include<opencv2/opencv.hpp>
#include<vector>
using namespace cv;
struct Feather
{
	int label;    
	int area;  
	Rect boundinbox; 
};
void illumination(Mat &src,Mat &overlay,const int &stepsize);
//---在头文件中最好不在前面定义命名空间,后面调用函数的时候在加上,eg: std::vector  
int bwlabel(Mat &src, Mat &dst, std::vector<Feather>&featherlist);
#endif