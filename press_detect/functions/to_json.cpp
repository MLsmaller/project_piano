#include<json/json.h>
#include<assert.h>   //调用assert()函数会用到
#include<typeinfo>   //用typeid(x).name()时需要包含这个库
#include<vector>
#include<fstream>
#include<numeric>
#include<cmath>
using namespace std;

Json::Value to_json(const string &img_name,vector<int>&pressed_key){

    Json::Value partner;
    partner["img_name"] = img_name;
    if (pressed_key.size()==0){
        partner["key"].append(0);
    }
    else{
        for (int i = 0; i < pressed_key.size();i++){
            partner["key"].append(pressed_key[i]);
        }
    }

    //根节点与子节点的转换
    //root[img_name] = Json::Value(partner);
    return partner;
}

void get_accuracy(const string &testJsonFile,const string &realTxtFile){
    //先将代码检测到的按键的Json文件读取出来-----------
    Json::Value root;
    Json::Reader reader;
    ifstream in;   //ifstream用于读入数据,ofstream写数据,open()为stream类的成员函数
    in.open(testJsonFile, ios::binary);  //以二进制方式打开文件
    assert(in.is_open());
    cout << testJsonFile << endl;
    vector<string> img_name;  //存放文件名字
    vector<vector<int>> key_w; //存放每一帧被按下的键
    //可以循环读取Json文件中的字典信息，然后将自己想要的存入到vector中去,对于数组,要循环读取逐个取出来
    if(reader.parse(in,root)){  //将json文件中的信息存入到根节点root中
        for (int i = 0; i < root.size();i++){
            string id = to_string(i);
            Json::Value img = root[id];
            img_name.push_back(img["img_name"].asString());
            vector<int> k;
            for (int j = 0; j < img["key"].size();j++){
                k.push_back(img["key"][j].asInt());
            }
            key_w.push_back(k);
            cout << img << endl;
        }
    }
    in.close();

    ifstream tin;
    tin.open(realTxtFile, ios::in);  //ios::in 读数据,ios::out 写数据
    assert(tin.is_open());
    char data[256];     //有时候出现段错误可能是因为数组内存过小,后面getline()可接受最大为256的字符
    //vector<string> data;
    while(tin.getline(data, 256, '\n')){   //.eof()函数判断文件是否读到尾部
        cout << data << endl;             //只要没读到最后一行的空格就继续读入
         //getline()逐行读数据,256为读取至多256个字符存在data数组中,'\n'为每行的结束标志符
        int size = sizeof(data) / sizeof(char);  //求数组的长度,sizeof(arr)/sizeof(数组类型)
        string str(data);
        int nPos = str.find_first_of(' ');
        string S_keyNum = str.substr(nPos+1);
        cout << S_keyNum << endl;
        vector<string> A_keyNum;
        int index = S_keyNum.find(' ');
        cout << index << endl;
        if(index==string::npos){
            A_keyNum.push_back(S_keyNum);
        }
        else{
            string a = S_keyNum.substr(0, index);
            cout << a << endl;
        }

            /*             if(!(S_keyNum[i]==' ')){
                cout << S_keyNum[i] << endl;
                //string number(S_keyNum[i]);
                //A_keyNum.push_back(number);
            } */
        //cout << A_keyNum[0] << endl;
        for (int i = 0; i < A_keyNum.size();i++){
            cout << "hah" << endl;
            cout << A_keyNum[i] << endl;
        }
        /*         for (int i = 0; i < str.size();i++){
            if(!(str[i]==' ')){
                file.push_back(to_string(str[i]));
            }
            else{
                str.substr()
            }
        } */
        /*         for (int i = 0; i < size;i++){
            cout << data[i] << endl;
            string s = to_string(data[i]);
            cout << s << endl;
        } */
        //cout << data << endl;
    }
    tin.close();
}


void Split(const string &src, const string &separator, vector<string> &dest) //字符串分割到数组
{
 
    //参数1：要分割的字符串；参数2：作为分隔符的字符；参数3：存放分割后的字符串的vector向量
 
	string str = src;
	string substring;
	string::size_type start = 0, index;
	dest.clear();
    vector<string> temp_dest(dest);
    index = str.find_first_of(separator,start);  //从位置start开始顺序查找第一个separator的位置
    do
	{
		if (index != string::npos)  //string::npos可表示是否查找到字符串的最后一个位置
		{    
			substring = str.substr(start,index-start); //str.substr()从位置start开始截取,截取的长度为index-start(默认是截取后面所有的)
            temp_dest.push_back(substring);   //将第一个字符串放入
			start =index+separator.size();
            index = str.find(separator,start);  //从上一个分隔符后面的字符位置开始下一轮查找(新的分隔符)
            if(start==index) 
                break;       //不要分隔符连在一起的情况,eg__  "  "
            cout << start << "aaaa"<<index << "hahahahha" << endl;
            //if (start == string::npos) break; 
            //string::npos是配合find/find_last_of()函数一起用的,当这些函数找不到字符则返回-1，即等于string::npos 
		}
	}while(index != string::npos);

    cout << "分隔线" << endl;

   
    cout << temp_dest.size() << endl;
    for (int i = 0; i < temp_dest.size();i++){
        cout << temp_dest[i]<< endl;
    }

    //the last part
	substring = str.substr(start);
    if(substring.find(separator)==string::npos){
        temp_dest.push_back(substring);
    }


        cout << temp_dest.size() << endl;
    for (int i = 0; i < temp_dest.size();i++){
        cout << temp_dest[i]<< endl;
        string temp_data = temp_dest[i];
/*         int ind = temp_data.find(separator);
        cout << temp_data << ind << endl; */
/*         if(ind==string::npos){
            dest.push_back(temp_dest[i]);
        } */

    }



}