#include<iostream>
#include<opencv2/opencv.hpp>
#include<vector>
#include<string>

#include<utils.hpp>

using namespace std;
using namespace cv;

// std::string base_path = "/home/data/cy/projects/piano/KJnotes/frames2/crop_img/0608.jpg";  //frames2.mp4
// std::string test_path = "/home/data/cy/projects/piano/KJnotes/frames2/crop_img/0417.jpg";  //frames2.mp4
// string save_path = "/home/data/cy/projects/piano/KJnotes/frames2/cnn/white_dif";
std::string base_path = "/home/data/cy/projects/piano/KJnotes/frames1/crop_img/3638.jpg";
std::string test_path = "/home/data/cy/projects/piano/KJnotes/frames1/crop_img/0015.jpg";
string w_save_path = "/home/data/cy/projects/piano/KJnotes/frames1/cnn/white_dif";
string b_save_path = "/home/data/cy/projects/piano/KJnotes/frames1/cnn/black_dif";


int main(){
    //--- C++可以直接这样相减得到那些图片,为啥python不行
    // string img_extern = "/home/data/cy/projects/piano/KJnotes/frames2/crop_img/*.jpg";
    string img_extern = "/home/data/cy/projects/piano/KJnotes/frames1/crop_img/*.jpg";
    vector<cv::String> file_list;
    glob(img_extern, file_list);

    cv::Mat base_img, cur_img;
    base_img = cv::imread(base_path);
    cv::cvtColor(base_img, base_img, cv::COLOR_BGR2GRAY);
    // int stepsize = 0;
    int frames = 0;
    for (int i = 0; i < file_list.size(); i++)
    {
        Mat cur_img = imread(file_list[i]);
        cvtColor(cur_img, cur_img, COLOR_BGR2GRAY);
        // illumination(base_img, cur_img, stepsize);   //---光照归一化
        Mat w_dif_img = base_img - cur_img;
        Mat b_dif_img = cur_img - base_img;
        char buf[80];
        char buf1[80];
        sprintf(buf1, "%s/%04d.jpg", b_save_path.c_str(),frames);
        sprintf(buf, "%s/%04d.jpg", w_save_path.c_str(),frames);
        cout << buf << endl;
        imwrite(buf, w_dif_img);
        imwrite(buf1, b_dif_img);
        frames++;
    }

    return 0;
}