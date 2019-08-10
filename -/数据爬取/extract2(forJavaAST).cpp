/**
本代码用于提取java文件中注释代码对
*/
#include <iostream>
#include <fstream>
#include <cstring>
#include <vector>
#include <stdio.h>
#include <sstream>
#include <io.h>
#include <string.h>
#include <string>
#include <algorithm>
#include <map> 
#include <unistd.h>
using namespace std;



int total = 0;
int filecount = 0;
int totalfile = 0;

/*
map<int,int> m;
void makeTag(){
	ifstream fin("C:\\Users\\27346\\Desktop\\test1.csv"); 
	string line; 
	while (getline(fin, line))   
	{
		int index1,index2;
		index1=line.find(',');
		index2=line.find(',',index1+1);
		
		int id,res;
	//	cout<<line.substr(index1-1)<<endl;
	//	cout<<line.substr(index1+1,index2-1)<<endl;
		id=atoi(line.substr(0,index1).c_str());
		res=atoi(line.substr(index1+1,index2-1).c_str()); 
		m[id]=res;

	}
} */

void getFiles(string path, vector<string>& files)
{
    //文件句柄
    long   hFile = 0;
    //文件信息，声明一个存储文件信息的结构体
    struct _finddata_t fileinfo;
    string p;//字符串，存放路径
    if ((hFile = _findfirst(p.assign(path).append("\\*").c_str(), &fileinfo)) != -1)//若查找成功，则进入
    {
        do
        {
            //如果是目录,迭代之（即文件夹内还有文件夹）
            if ((fileinfo.attrib &  _A_SUBDIR))
            {
                //文件名不等于"."&&文件名不等于".."
                //.表示当前目录
                //..表示当前目录的父目录
                //判断时，两者都要忽略，不然就无限递归跳不出去了！
                if (strcmp(fileinfo.name, ".") != 0 && strcmp(fileinfo.name, "..") != 0)
                    getFiles(p.assign(path).append("\\").append(fileinfo.name), files);
            }
            //如果不是,加入列表
            else
            {
                files.push_back(p.assign(path).append("\\").append(fileinfo.name));
            }
        } while (_findnext(hFile, &fileinfo) == 0);
        //_findclose函数结束查找
        _findclose(hFile);
    }
}


string IntToStr(int n){
    std::stringstream newstr;
    newstr<<n;
    return newstr.str();
}

string extract(string javafilepath){
    filecount++;
    if (filecount % 1000 == 0)
        cout<< filecount <<"/"<< totalfile << endl;

    FILE *fp;
    string strLine;
    string com,cod;
    string extract_result;

    extract_result = "";

    char str[300];

        fp = fopen(javafilepath.c_str(), "r");
        if (fp == NULL){
            cout<<"Error: file can not be opened:";
        } else{
            //cout<<"Open File: "<<javafilepath<<endl;
        }

        int line = 0;
        int fail = 0;
        while (1){
			fail = 0;
			int comFlag = 0;
            fgets(str,200,fp);
            strLine = str;
            line++;

            if (feof(fp)){
                break;
            }
            //找 /*开头的注释
            if (strLine.find("/*") != -1){
                int fff = 0;
                for (int kk = 0; kk < strLine.find("/*"); kk++){
                    char cc = strLine[kk];
                    if (cc>='a'&& cc<='z'){
                        fff = 1;
                        break;
                    }
                    if (cc>='A'&& cc<='Z'){
                        fff = 1;
                        break;
                    }
                }
                if (fff == 1)
                    continue;

                //找全所有注释，拼接在一起
                com = strLine;

                if (strLine.find("*/") == strLine.npos)
                while (1){
                	
                	//处理non-Javadoc 
                	if(strLine.find("non-Javadoc")!=strLine.npos){
                		fail = 1;
					}
					
                	//处理无用注释，已验证 ，/**加上回车是4个字符 ，还有前面有个tab的情况 
					if (strLine.size()>5 && strLine.find("@author")==strLine.npos && strLine.find("Created by")==strLine.npos &&  \
					strLine.find("@date")==strLine.npos &&strLine.find("@version")==strLine.npos) {
						comFlag = 1;
					//	cout<<strLine<<endl;
					//	cout<<strLine.size()<<endl;
					}	
					
                    fgets(str,200,fp);
                    line++;
                    strLine =str;
                    if (feof(fp)){
                        com = "";
                        break;
                    }
                    if (strLine.empty())
                        continue;

                    com = com + strLine;

                    if (strLine.find("*/") != strLine.npos)
                        break;
                }

                if (com.find("Copyright") != strLine.npos ||
                    com.find("copyright") != strLine.npos){
                    continue;
                }

                if (com == "")
                    continue;
              //  cout<<comFlag<<endl;
                if (!comFlag) {
                	continue;//加快计算速度 
                	//fail = 1;
                }

                //开始找代码
                cod = "";
                int count1 = 0;
                int count2 = 0; 

                int flag = 0;
                int codeline = 0;
                
                string lastStrLine="";
                strLine="";
                
                //左括号必须先出现  } catch (InterruptedException ex) {
                int zuoFirst=0;
                int zuoFlag=0;
                
                while (1){
                	
                	//记录上一行 
                	lastStrLine=strLine;
                	
                    fgets(str,200,fp);
                    if(str=="") continue;
                    line++;
                    codeline++;
                    strLine = str;
                    cod = cod + strLine;

                    if (feof(fp)){
                        break;
                    }
                    
                    if (strLine.find("@") != strLine.npos)
                        continue;
                      
                    if (strLine.find("pubilc abstract") != strLine.npos || strLine.find("protected abstract") != strLine.npos){
                    	fail=1;
                    	break;
					}
                      
                    //处理一些行出现@和大括号的情况 
                    /*
                    if (strLine[0] == '@') 
                    	continue;
                    */	
                    if (strLine.find("{") != strLine.npos){
                    	
                    	if(zuoFirst==0){
                    		zuoFirst=1;
                    		zuoFlag=1;
						}
                    	
						 
                    	//向上调整，避免第一行出现多个{ 
                    	if (count1 == 0) {
                    		if(strLine.find("{") != 0){
							
                        		if (strLine.find(" class ") != strLine.npos || strLine.find("interface") != strLine.npos ) {
                        			fail = 1;
                        		}
                        	}
                        	else{
                        		if (lastStrLine.find(" class ") != lastStrLine.npos || lastStrLine.find("interface") != lastStrLine.npos ) {
                        			fail = 1;
                        		}
							}
                        	//cout<<strLine<<" "<<fail<<endl; 
                        }
                        
                        flag = 1;
                        count1 += count(strLine.begin(), strLine.end(), '{');
                        
                    }
                    if ((zuoFlag && strLine.find("}") != strLine.npos && strLine.find("}") > strLine.find("}") ) || (zuoFirst && !zuoFlag && strLine.find("}") != strLine.npos) )
                        count2 += count(strLine.begin(), strLine.end(), '}');
                    
                   // cout<<strLine<<" "<<count1<<" "<<count2<<endl;
                    
                    if ((count1-count2) == 0 && flag == 1)
                        break;
                        
                    zuoFlag=0;
                }
                if (codeline>1 && codeline <= 40){
                	if (!fail && count1+count2<codeline) {//避免代码内部为空 
                		total ++;
	                    extract_result += "#No. "+ IntToStr(total) + "\n" +
	                                      "#File: "+javafilepath+"\n"+
	                                      "#Comment:"+"\n"+
	                                      com+"\n"+
	                                      "#Code:"+"\n"+
	                                      cod+"\n";
                	}
                } 
            }
        }
    fclose(fp);
    return extract_result;
}

int isJavaFile(string file){
    if (file.substr(file.length()-5, file.length()-1) == ".java")
        return 1;
    else
        return 0;
}

int isDuplicatedFile(string file) {
	if (file.find("(") != file.npos) 
		return 1;
	else 
		return 0;
}

int main(){
    const char* outputfile = "testout.txt";

    //char * filePath = "\\home\\wdz\\桌面\\未命名文件夹\\data_zip";
    char * filePath = "E:\\bishe\\1";
    vector<string> files;
    ////获取该路径下的所有文件
    getFiles(filePath, files);

    ofstream outfile;
    outfile.open(outputfile);
    cout<< "文件总数：" << files.size()<<endl;
    totalfile = files.size();
    for (int i = 0; i < files.size(); i++)
    if (isJavaFile(files[i])){
    	// 去掉重复的文件（名字里带括号的） 
    	if (!isDuplicatedFile(files[i])) { 
    		outfile<<extract(files[i]);
    	}
    }
    outfile.close();
    return 0;
}
