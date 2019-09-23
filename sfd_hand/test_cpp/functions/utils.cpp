#include<iostream>
#include<opencv2/opencv.hpp>
#include<vector>
#include<string>

using namespace std;
using namespace cv;
//--------光照归一化操作-----------
void illumination(Mat &src,Mat &overlay,const int &stepsize){
	int width = src.cols;
	int height = src.rows;  
	int v;
	int pixelSize = src.channels();    //每个像素多少个字节
	int linesize = width * pixelSize;  //每一行需要这么多字节存储
	vector<vector<int> >num(height,vector<int>(linesize,0));  //存放v
	for (int i = 0; i < height; i++)
	{
		uchar *data1=src.ptr<uchar>(i);
		uchar *data2=overlay.ptr<uchar>(i);
		for (int j = 0; j < linesize; j++)
		{
			v = int(data2[j]-data1[j]);
			num[i].push_back(v);
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