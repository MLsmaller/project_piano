#include<iostream>
#include<vector>
#include<string>
#include<opencv2/opencv.hpp>

using namespace std;
using namespace cv;

//-----用c++的霍夫变换可以检测出那些直线------
int main(){

    Mat midImage, dstImage, final_img, src;
    src = imread("/home/data/cy/projects/piano/frame/video1_whole_frame/0100.jpg");

    final_img = src.clone();
    int width, height;
    width = src.cols;
    height = src.rows;
    cvtColor(src, src, COLOR_BGR2GRAY);
    blur(src, src, Size(5, 5));
    Canny(src, midImage, 50, 200, 3); //进行一此canny边缘检测
    imwrite("../canny.jpg", midImage);
    //canny边缘检测后如果白色像素占图片总像素值大于某一阈值,认为该图片中包含钢琴(有些视频开头不是马上弹钢琴)

    vector<Vec4i> lines;
    cvtColor(midImage, dstImage, COLOR_GRAY2BGR);
    HoughLinesP(midImage, lines, 1, CV_PI / 180, 320, (0.9)*width, width);  //想要结果为小数记得加.0,eg:(2.0/3)
    //260:阈值,大于阈值的线段才可以被检测出来; (2.0/3)*width:最低线段的长度,大于才能显示出来; width:允许同一行点与点之间连接起来的最大的距离
    //cout << "检测到的直线数量为: "<<lines.size() << endl;
    for(int i=0;i<lines.size();i++){
        Vec4i l = lines[i];
        line(final_img, Point(l[0], l[1]), Point(l[2], l[3]), Scalar(0, 0, 255), 1, CV_AA);

    }
    imwrite("../test_cpp.jpg", final_img);

}
