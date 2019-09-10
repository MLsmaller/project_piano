#ifndef _GET_KEYBOARD_H
#define _GET_KEYBOARD_H
#include<opencv2/opencv.hpp>
using namespace cv;
using namespace std;

Mat remove_region(Mat &result);
Mat keyboard(Mat &src, vector<Rect> &box_keyboard, float &ratio, vector<Vec4i> &lines);
void key_loc(const Mat &img,vector<Rect> &black_box,vector<double> &white_loc,vector<int> &area);
int count_pixel(Mat &img);
float count_brightness(Mat &img);
int find_base(Mat &img, const int &index, const vector<string> &fn,int &best_index);
//void draw_whole_keys(const Mat &img, const vector<double> &white_loc, const vector<Rect> black_box,
                     //const int&b_height);



#endif
