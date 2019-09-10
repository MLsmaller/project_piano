#ifndef _DETECT_KEY_H_
#define _DETECT_KEY_H_
#include<opencv2/opencv.hpp>
using namespace std;
using namespace cv;
int draw_box(double &white_loc, vector<Rect> &black_box);
vector<int> detect_w(Mat &src_rgb, Mat &img, vector<Point> &hand_point,
                     const vector<double> &white_loc, 
                     const Rect &box, const float &ratio, vector<int> &pre_w ,
                     vector<Rect> &total_top, vector<Rect> &total_bottom);
vector<int> detect_w1(Mat &src_rgb,Mat &img,vector<Point>&hand_point,
                        const vector<double>&white_loc,vector<Rect>&black_box,
                        const Rect &box,const float &ratio,vector<int> &pre_w,
                        vector<Rect> &total_top,vector<Rect> &total_bottom);

void find_box(Mat &base_img_rgb, vector<double> &white_loc, 
                vector<Rect> &black_box, vector<Rect> &total_top, vector<Rect> &total_bottom);
#endif