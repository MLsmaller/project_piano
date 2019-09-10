#include<opencv2/opencv.hpp>
#include<iostream>
#include<vector>
using namespace std;
using namespace cv;




//-----找到离白键最近的那个黑键------
int draw_box(double &white_loc,vector<Rect> &black_box){
    vector<double> diffs;
    for (int i = 0; i < black_box.size();i++){
        double diff = abs(black_box[i].tl().x - white_loc);
        diffs.push_back(diff);
    }
    //求vector中元素的最小值
    vector<double>::iterator smallest = min_element(begin(diffs), end(diffs));
    int index = distance(begin(diffs), smallest);
    return index;
}

vector<int> detect_w(Mat &src_rgb,Mat &img,vector<Point>&hand_point,
                        const vector<double>&white_loc,
                        const Rect &box,const float &ratio,vector<int> &pre_w,
                        vector<Rect> &total_top,vector<Rect> &total_bottom){
	vector<Point>hand_tip;   //存放手指指尖的位置
    int b_height=img.rows;   //如果只想要指尖的位置是不是可以用跑指尖的模型来跑keypoint
    int b_width=img.cols;
    if(hand_point.size()>1){
        for(int i=0;i<hand_point.size();i++){
            if(i==4||i==8||i==11||i==15||i==20){
                hand_tip.push_back(hand_point[i]);  //从大拇指到小指
            }
        }
        for(int i=0;i<hand_tip.size();i++){  //循环每个手指
            if(hand_tip[i]==Point(0,0)){  //如果该关键点没检测到
                continue;
            }
            else{
    //将关键点坐标转换为在只包含钢琴图片的坐标中
                Point center=Point(hand_tip[i].x-box.tl().x,hand_tip[i].y-box.tl().y);
                circle(src_rgb,center,5,Scalar(0,0,255),-1);
                Point hand_loc=hand_tip[i];
                //判断手的坐标是否在钢琴上
                double new_x=hand_loc.x-box.tl().x;
                double new_y=hand_loc.y-box.tl().y;
                int offset=15;
    //减10是为了让有些帧中手指的关键点能够显示在钢琴上,有些刚好在钢琴下面差一点点
                if(new_x>0&&new_y>0&&new_x<b_width&&((new_y-10)<b_height)){  
                    //判断手的位置在哪个白键上
                    for(int p=0;p<white_loc.size()-1;p++){   //循环每个白键
                        Rect current_top=total_top[p];
                        Rect current_bottom = total_bottom[p];
                        double white_x=white_loc[p];
                        double white_width=white_loc[p+1]-white_x;
                        int w_count=0;
                        int area_w=0;
                        if((new_x>white_x)&&(new_x<white_x+white_width)){
                        //手在第p+1个白键上
                            cout<<"第 "<<i<<" 个手指在第 "<<p+1<<"个白键上"<<endl;
                            for(int m=0;m<b_height;m++){
                                uchar *data_w=img.ptr<uchar>(m);
                                for(int n=0;n<b_width;n++){
                        //该关键点上方的白色像素占关键点上方区域比例的多少
                        //offset是因为有时候关键点附近那块连带着的白色像素过多,因此向上移动一点(如果关键点准确的话较好)
                        //是不是考虑一下其中某个手指才需要进行移动加上offset呢

                                    if((n>white_x)&&(n<white_x+white_width)&&(m<(new_y-offset))){
                                        if(int(data_w[n])==255){
                                            w_count++;
                                        }
                                    }
                                    if((n>white_x)&&(n<white_x+white_width)&&(m<(new_y-offset))){
                                        area_w++;
                                    }
                                }
                            }
                            if(w_count>int(ratio*area_w)){
                                Rect white_box=Rect(white_x,0,0.5*white_width,0.5*b_height);
                                rectangle(src_rgb,white_box,Scalar(255,0,0),-1);
                                cout<<"白键 "<<p+1<<"被按下"<<endl;
                                pre_w.push_back(p+1);
                            }
                            cout<<"白色像素为: "<<w_count<<endl;
                            cout<<"区域面积为: "<<area_w<<endl;
                        }
                    }
                }
            }
        }
    }
    return pre_w;
}

vector<int> detect_w1(Mat &src_rgb,Mat &img,vector<Point>&hand_point,
                        const vector<double>&white_loc,vector<Rect>&black_box,
                        const Rect &box,const float &ratio,vector<int> &pre_w,
                        vector<Rect> &total_top,vector<Rect> &total_bottom){
	vector<Point>hand_tip;   //存放手指指尖的位置
    int b_height=img.rows;   //如果只想要指尖的位置是不是可以用跑指尖的模型来跑keypoint
    int b_width=img.cols;
    vector<Point2f>pixel_ratio;
    vector<float> pixel;
    vector<int>pressed_num;
    //vecot<int>white_nums;
    //----下面为容易误检的相邻按键,直接不画，画的时候也有判断,只是有时候会错误------
    int white_nums[]={2,5,12,19,26,33,40,47,9,16,23,30,37,44,51};
    int arr_length=sizeof(white_nums)/sizeof(int);
    if(hand_point.size()>1){
        for(int i=0;i<hand_point.size();i++){
            if(i==4||i==8||i==11||i==15||i==20){
                if((i==11)||(i==15)){   
                    if(not(hand_point[i]==Point(0,0))&&not((hand_point[i+1]==Point(0,0)))){
                        double index_y=hand_point[i].y-box.tl().y;
                        //-----对于手指坐标在图片上面3/5区域才选择最上面的那个关键点来判断,因为有时候指尖的那个关键点会跑到其他位置去--
                        if((hand_point[i+1].y<hand_point[i].y)&&(index_y>0&&((index_y-10)<(3.0/5)*b_height))){
                            hand_tip.push_back(hand_point[i+1]);
                        }
                        else{
                            hand_tip.push_back(hand_point[i]);
                        }
                    }
                }
                else{
                    hand_tip.push_back(hand_point[i]);  //从大拇指到小指(应该统计该手指上纵坐标最小的点)

                }
            }
        }
        for(int i=0;i<hand_tip.size();i++){  //循环每个手指
            if(hand_tip[i]==Point(0,0)){    //如果该关键点没检测到
                continue;
            }
            else{
    //将关键点坐标转换为在只包含钢琴图片的坐标中
                Point center=Point(hand_tip[i].x-box.tl().x,hand_tip[i].y-box.tl().y);
                circle(src_rgb,center,5,Scalar(0,0,255),-1);
                Point hand_loc=hand_tip[i];
                //判断手的坐标是否在钢琴上
                double new_x=hand_loc.x-box.tl().x;
                double new_y=hand_loc.y-box.tl().y;
                int offset=15;
                int extent_step=2;
    //减10是为了让有些帧中手指的关键点能够显示在钢琴上,有些刚好在钢琴下面差一点点
                if(new_x>0&&new_y>0&&new_x<b_width&&((new_y-10)<b_height)){  
                    //判断手的位置在哪个白键上
                    for(int p=0;p<white_loc.size()-1;p++){   //循环每个白键
                        Rect current_top=total_top[p];
                        Rect current_bottom = total_bottom[p];
                        double white_x=white_loc[p];
                        double white_width=white_loc[p+1]-white_x;
                        int w_count=0;
                        int area_w=0;
                        if((new_x>white_x)&&(new_x<white_x+white_width)){
                        //手在第p+1个白键上
                            //cout<<"第 "<<i<<" 个手指在第 "<<p+1<<"个白键上"<<endl;
                            for(int m=0;m<b_height;m++){
                                uchar *data_w=img.ptr<uchar>(m);
                                for(int n=0;n<b_width;n++){
                        //该关键点上方的白色像素占关键点上方区域比例的多少
                        //offset是因为有时候关键点附近那块连带着的白色像素过多,因此向上移动一点(如果关键点准确的话较好)
                        //是不是考虑一下其中某个手指才需要进行移动加上offset呢
                        //-----这里没有区分大拇指的时候就统计2/3上面的像素,因为这里的dif图像都还可以
                                    float diff_line = new_y - offset;  //关键点纵坐标
                                    //float div = 1.0 / 3 * b_height;     //分隔线
                                    float div = 2.0 / 5 * b_height;
                                    if(diff_line>div){
                                        if((n>white_x-extent_step)&&(n<white_x+white_width+extent_step)&&(m<(div))){
                                            if(int(data_w[n])==255){
                                                w_count++;
                                            }
                                        }
                                        if((n>white_x-extent_step)&&(n<white_x+white_width+extent_step)&&(m<(div))){
                                            area_w++;
                                        }
                                    }
                                    else{
                                        if((n>white_x-extent_step)&&(n<white_x+white_width+extent_step)&&(m<(new_y-offset))){
                                            if(int(data_w[n])==255){
                                                w_count++;
                                            }
                                        }
                                        if((n>white_x-extent_step)&&(n<white_x+white_width+extent_step)&&(m<(new_y-offset))){
                                            area_w++;
                                        }
                                    }
                                }
                            }
                            if(w_count>int(ratio*area_w)){
                                vector<int> ::iterator it1;
                                it1 = find(pressed_num.begin(), pressed_num.end(), p+1);
                                //----如果白键已经存入vector内就不再存储了---
                                if(it1==pressed_num.end()){
                                    float final_pixel=float(w_count)/area_w;
                                    pixel_ratio.push_back(Point2f(final_pixel,p+1));
                                    pixel.push_back(final_pixel);
                                    pressed_num.push_back(p+1);
                                    //sort(pressed_num.begin(),pressed_num.end(),less<int>());
                                    cout<<"白键 "<<p+1<<"被按下"<<endl;
                                }
                            }
                            cout << "当前白键为: " << p + 1 << endl;
                            cout<<"白色像素为: "<<w_count<<endl;
                            //cout<<"区域面积为: "<<area_w<<endl; 
                            cout<<"白色像素所在比例为 :"<<float(w_count)/area_w<<endl;
                        }
                    }
                }
            }
        }
    }

/*     //------需要去除一下重复的元素,因为有时候关键点离得比较近导致都在同一个白键区域内-----
    vector<int>::iterator ite = unique(pressed_num.begin(), pressed_num.end());
    pressed_num.erase(ite, pressed_num.end()); */
    pre_w.assign(pressed_num.begin(), pressed_num.end()); //拷贝一份pressed_num

    cout << "pressed_num size 为: " << pressed_num.size() << endl;
    for(int m=0;m<pressed_num.size();m++){
        int index=pressed_num[m];
        float thres = 0.01;   //如果相邻的两个白键的像素所占比例差值大于0.02,则认为隔壁的那个键没有被按下
        for(int n=0;n<arr_length;n++){
            if(white_nums[n]==index){
                vector<int> ::iterator it;
                it = find(pressed_num.begin(), pressed_num.end(), index + 1);
                if(it!=pressed_num.end()){
                    int n_pos = distance(pressed_num.begin(), it);
                    float cur_pixel = pixel[m];
                    float next_pixel = pixel[n_pos];
                    float dif = cur_pixel - next_pixel;
                    pre_w.erase(pre_w.begin() + n_pos);     //直接舍弃那些相邻的试一下,看一下那种按键多不多?? 
/*                     if((cur_pixel>next_pixel)&&(dif>thres)){
                        pre_w.erase(pre_w.begin() + n_pos);
                    } */
                    cout << "cur_pixel is : " <<pixel[m]<<" next_pixel is : "<<pixel[n_pos]<< endl;
                }
            }
        }
        //cout<<pressed_num[m]<<endl;
    }

    for (int i = 0; i < pre_w.size();i++){
        int w_index = pre_w[i];
        Rect cur_box1 = total_bottom[w_index-1];
        Rect cur_box2 = total_top[w_index-1];
        rectangle(src_rgb, cur_box1, Scalar(0, 0, 255), 1);
        rectangle(src_rgb, cur_box2, Scalar(0, 0, 255), 1);
    }
    return pre_w;
}

//-----找到每个白键所在区域的那个框框---------------
void find_box (Mat &base_img_rgb, vector<double> &white_loc, vector<Rect> &black_box, vector<Rect> &total_top, vector<Rect> &total_bottom){
    
    int b_height = base_img_rgb.rows;  //base_img.rows
    int b_width=base_img_rgb.cols;   
    for (int p = 1; p < white_loc.size() ;p++){
        
        double white_x = white_loc[p-1];
        double white_width=white_loc[p]-white_x;
        //line(base_img_rgb, Point2f(white_x, 0), Point2f(white_x, b_height), Scalar(0, 0, 255), 1, CV_AA);
        //imwrite("../white_line.jpg", base_img_rgb);
        //-----前面两个键不在周期规律内-----
        if(p==1){
            Rect top_box=Rect(white_x, 0, black_box[p-1].tl().x-white_x, 1.1*black_box[p-1].height);
            Rect bottom_box=Rect(white_x, 1.1*black_box[p-1].height, white_width, b_height-1.1*black_box[p-1].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box);
        }
        else if(p==2){
            Rect top_box=Rect(black_box[p-2].br().x, 0, white_loc[p]-black_box[p-2].br().x, 1.1*black_box[p-2].height);
            Rect bottom_box=Rect(white_x, 1.1*black_box[p-2].height, white_width+2, b_height-1.1*black_box[p-2].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box);
        }
        else if((p==3||((p-3)%7==0)&&p<52)||(((p==6||((p-6)%7==0)&&p<52)))){
            int index = draw_box(white_x, black_box);
            Rect top_box=Rect(white_x+1, 0, black_box[index].tl().x-white_x-1, 1.1*black_box[index].height);
            Rect bottom_box=Rect(white_x, 1.1*black_box[index].height, white_width+2, b_height-1.1*black_box[index].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box);         
        }
        else if((p==4||((p-4)%7==0)&&p<52)||(((p==7||((p-7)%7==0)&&p<52)))||(((p==8||((p-8)%7==0)&&p<52)))){
            int index = draw_box(white_x, black_box);
            Rect top_box=Rect(black_box[index].br().x+1, 0, black_box[index+1].tl().x-black_box[index].br().x-1, 1.1*black_box[index].height);
            Rect bottom_box=Rect(white_x, 1.1*black_box[index].height, white_width+2, b_height-1.1*black_box[index].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box);
        }
        else if((p==5||((p-5)%7==0)&&p<52)||(((p==9||((p-9)%7==0)&&p<52)))||(((p==8||((p-8)%7==0)&&p<52)))){
            int index = draw_box(white_x, black_box);
            Rect top_box=Rect(black_box[index].br().x+1, 0, white_loc[p]-black_box[index].br().x-1, 1.1*black_box[index].height);
            Rect bottom_box=Rect(white_x, 1.1*black_box[index].height, white_width+2, b_height-1.1*black_box[index].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box);
        }
        //----最后一个框
        else{
            Rect top_box=Rect(white_x+1, 0, white_loc[p]-white_x-1, 1.1*black_box[35].height);
            Rect bottom_box=Rect(white_x+1, 1.1*black_box[35].height, white_loc[p]-white_x-1, b_height-1.1*black_box[35].height);
            total_top.push_back(top_box);
            total_bottom.push_back(bottom_box); 
        }

    }
    //cout << total_top.size() << endl;
    for (vector<Rect>::iterator iter = total_top.begin(); iter < total_top.end();iter++){
        rectangle(base_img_rgb, *iter, Scalar(0, 0, 255), 1);
    }
    for (int i = 0; i < total_bottom.size();i++){
        Rect cur_box = total_bottom[i];
        rectangle(base_img_rgb, cur_box, Scalar(0, 0, 255), 1);
        string text = to_string(i);
        putText(base_img_rgb, text, Point(total_bottom[i].tl().x + 5, b_height), FONT_HERSHEY_COMPLEX, 0.5, Scalar(255, 0, 0), 2);
    }
              
    imwrite("../test_rec.jpg", base_img_rgb);

}