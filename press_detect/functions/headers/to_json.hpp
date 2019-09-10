#ifndef _TO_JSON_H_
#define _TO_JSON_H_
using namespace std;
Json::Value to_json(const string &img_name, vector<int> &pressed_key);
void get_accuracy(const string &testJsonFile,const string &realTxtFile);
void Split(const string &src, const string &separator, vector<string> &dest);
#endif