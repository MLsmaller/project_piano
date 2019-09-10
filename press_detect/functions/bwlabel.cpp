#include<opencv2/opencv.hpp>
#include<bwlabel.hpp>
#include<string>
#include<iostream>
#include<vector>
#include<stack>
using namespace cv;
using namespace std;

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

//边缘区域检测算法,检测连通区域,黑键
int bwlabel(Mat &src, Mat &dst, vector<Feather>&featherlist)
{
	int rows = src.rows;
	int cols = src.cols;
	int labelValue = 0;
	Point seed, neighbor;
	stack<Point>pointStack;  
	int area = 0;       
	int leftBoundary = 0; 
	int rightBoundary = 0;
	int topBoundary = 0;
	int bottomBoundary = 0;
	Rect box;  
	Feather feather;
	featherlist.clear();  
	dst.release();   
	dst = src.clone();
	for (int i = 0; i < rows; i++)
	{
		uchar *pRow = dst.ptr<uchar>(i);   
		for (int j = 0; j < cols; j++)
		{
			if (pRow[j] == 0)          
			{
				area = 0;
				labelValue++;
				seed = Point(j, i);    //(j,i)才是坐标,rows对应的是height,cols对应的是width
				dst.at<uchar>(seed) = labelValue;
				pointStack.push(seed);
				area++;
				leftBoundary = seed.x;
				rightBoundary = seed.x;
				topBoundary = seed.y;
				bottomBoundary = seed.y;

				while (!pointStack.empty())
				{

					neighbor = Point(seed.x + 1, seed.y);  
					if ((seed.x != (cols - 1)) && (dst.at<uchar>(neighbor) == 0))   
					{
						dst.at<uchar>(neighbor) = labelValue;
						pointStack.push(neighbor);
						area++;
						if (rightBoundary < neighbor.x) {
							rightBoundary = neighbor.x;
						}

					}

					neighbor = Point(seed.x, seed.y + 1);    //下面元素
					if ((seed.y != (rows - 1)) && (dst.at<uchar>(neighbor) == 0))
					{
						dst.at<uchar>(neighbor) = labelValue;
						pointStack.push(neighbor);

						area++;
						if (bottomBoundary < neighbor.y) {
							bottomBoundary = neighbor.y;
						}
					}

					neighbor = Point(seed.x - 1, seed.y);    //左边元素
					if ((seed.x != 0) && (dst.at<uchar>(neighbor) == 0))
					{
						dst.at<uchar>(neighbor) = labelValue;
						pointStack.push(neighbor);

						area++;
						if (leftBoundary > neighbor.x) {
							leftBoundary = neighbor.x;
						}
					}

					neighbor = Point(seed.x, seed.y - 1);      //上边元素
					if ((seed.y != 0) && (dst.at<uchar>(neighbor) == 0))
					{
						dst.at<uchar>(neighbor) = labelValue;
						pointStack.push(neighbor);

						area++;
						if (topBoundary > neighbor.y) {
							leftBoundary = neighbor.y;
						}
					}

					seed = pointStack.top();   //取栈顶元素并出栈
					pointStack.pop();
				}
				box = Rect(leftBoundary, topBoundary, rightBoundary - leftBoundary, bottomBoundary - topBoundary);  
				rectangle(src, box, (0,0,255));
				feather.area = area;
				feather.boundinbox = box;
				feather.label = labelValue;
				featherlist.push_back(feather);

			}
		}
	}
	return labelValue;
}
