#include<opencv2/opencv.hpp>
#include<iostream>
#include<string>
#include<vector>
#include <iomanip> 
#include <cstdio>
#include <sstream>
#include <fstream>
#include<json/json.h>
#include<ctime>

using namespace  cv;
using namespace std;

int main(int argc,char const *argv[]){
    string json_name="/home/lj/projects/detection/detectHand/sfd_hand/hand_point2.json";
    Json::Reader reader;
    Json::Value root;
    ifstream in;
    in.open(json_name.c_str(), ios::binary);
    if(!in.is_open()){
        cout<<"Error open json file\n";
    }
    vector<Point>finger_loc;
    if(reader.parse(in,root)){
        Json::Value data=root["value"];
        int size=data.size();
        string filename;
        vector<vector<Point>>left_point;
        vector<vector<Point>>right_point;
        for(int i=0;i<size;i++){
            filename =data[i]["filename"].asString();
            cout<<filename<<endl;
            Json::Value point_l=data[i]["keypoint_l"];   //Json文件直接用索引取某个值要加个U,用for循环时又不用
            Json::Value point_r=data[i]["keypoint_r"];
            int length_l=point_l.size();
            int length_r=point_r.size();
            vector<Point>hand_l;
            vector<Point>hand_r;
            if (length_l>0){
                for(int i=0;i<length_l;i++){
                    if(point_l[i].size()==0){
                        hand_l.push_back(Point(0,0));
                    }
                    else{
                        hand_l.push_back(Point(point_l[i][0U].asInt(),point_l[i][1U].asInt()));
                    }  
                }
            }
            else{
                hand_l.push_back(Point(0,0));
            }
            if (length_r>0){
                for(int i=0;i<length_r;i++){
                    if(point_r[i].size()==0){
                        hand_r.push_back(Point(0,0));
                    }
                    else{
                        hand_r.push_back(Point(point_r[i][0U].asInt(),point_r[i][1U].asInt()));
                    }  
                }
            }
            else{
                hand_r.push_back(Point(0,0));
            }
            left_point.push_back(hand_l);
            right_point.push_back(hand_r);
        } 
    }
    return 0;
}
