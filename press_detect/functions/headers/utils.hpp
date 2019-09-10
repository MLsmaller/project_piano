#ifndef _UTILS_H_
#define _UTILS_H_
#include<opencv2/opencv.hpp>
using namespace cv;
using namespace std;
void background_subtract(Mat &base,Mat &img_keyboard,Mat &black,Mat &white,const int &threshold);
void get_keypoint(const string &json_name,vector<vector<Point> >&left_point,vector<vector<Point> >&right_point,vector<string>&img_name);
void video_to_frame(const string &video_path, const string &save_path, const int &frameTostop,bool conver);
//vector<Point>ReadJson(string &json_name);
#endif