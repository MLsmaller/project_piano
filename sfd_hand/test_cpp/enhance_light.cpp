#include<iostream>
#include<opencv2/opencv.hpp>

using namespace std;
using namespace cv; 

// Normalizes a given image into a value range between 0 and 255.  
Mat norm(const Mat& src) {
	// Create and return normalized image:  
	Mat dst;
	switch (src.channels()) {
	case 1:
		cv::normalize(src, dst, 0, 255, NORM_MINMAX, CV_8UC1);
		break;
	case 3:
		cv::normalize(src, dst, 0, 255, NORM_MINMAX, CV_8UC3);
		break;
	default:
		src.copyTo(dst);
		break;
	}
	return dst;
}

 
int main()
{
	Mat image,X,I;
    Mat final_img;
    string img_path = "/home/data/cy/projects/piano/initial_video/frame/video1_whole_frame/0561.jpg";
    image = imread(img_path);

	image.convertTo(X, CV_32FC1); //转换格式
	float gamma = 0.5;
    cout << X << endl;
    pow(X, gamma, I);
    cout << I << endl;
    final_img = norm(I);
    imwrite("/home/cy/projects/github/project_piano/sfd_hand/piano_functions/imgs/9111.jpg", final_img);
    return 0;
}
