# -*- coding: utf-8 -*- 
import re
import sys
from nltk.stem import WordNetLemmatizer
reload(sys)
sys.setdefaultencoding('utf-8')

import imp  
import io
imp.reload(sys)  

def getargvdic(argv):
	optd = {}
	while argv:
		if argv[0][0] == '-':
			optd[argv[0]] =argv[1]
			argv = argv[2:]
		else:
			argv = argv[1:]
	return optd


def GetListOfStopWords(filepath):
    f_stop = open(filepath)
    try:
        f_stop_text = f_stop.read().replace('\r','')
        f_stop_text = unicode(f_stop_text, 'utf-8').encode('utf-8')
    finally:
        f_stop.close()
    f_stop_seg_list = f_stop_text.split('\n')

    return f_stop_seg_list

#resolve the variable 
def resolve(check_str):
	list_resolve = []
	tag1 = -1
	tag2 = -1
	index = 0
	for i in range(len(check_str)):
		
		tag2 = tag1

		if check_str[i].islower():
			tag1 = 1
		elif  check_str[i].isupper():
			tag1 = 2
		elif check_str[i].isdigit():
			continue
		else:
			if i > index:
				list_resolve.append(check_str[index:i])
			list_resolve.append(check_str[i])
			index = i+1 
		
		if  tag1 == 1 and tag2 == 2 and i > index + 1:
			list_resolve.append(check_str[index:i-1])
			index = i-1
		
		if tag1 == 2 and tag2 == 1:
			list_resolve.append(check_str[index:i])
			index = i
	if index < len(check_str):
		list_resolve.append(check_str[index:])
	
	return list_resolve

#去除s中所有l，r及中间内容
def remove(s, l, r):
	pos = s.find(l)
	while pos != -1:
		pos2 = s.find(r,pos)
		if pos2 != -1:
			s = s[0:pos] + s[pos2+1:len(s)]
			pos = s.find(l)
		else:
			break
	pos = s.find(l)
	if pos != -1:
		s = s[:pos]
	return s

#检查是否只包含英文字母和特定字符
def check_only_english(s):
    
    for i in range(len(s)):
        if 'a' <= s[i] <= 'z' or 'A' <= s[i] <= 'Z' or '0' <= s[i] <= '9' or s[i] in {' ', ',', '.','-','\'',':' }:
            continue
        else:
            return False
    return True

def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def remove_chinese(check_str):
    
    nstr = check_str
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
	 
            nstr = nstr.replace(ch, '')
    
    #nstr = re.sub('[^0-9a-zA-Z]',' ',check_str)
    return nstr


def deal_code(s):
	
	if s.find('class')!= -1 or s.find('enum')!=-1 or s.find('interface')!=-1 or s.count('private')+s.count('public') >= 2:
		return ""
	for i in range(10):
		pos1 = s.find('/*')
		pos2 = s.find('*/')
		if pos1 != -1 and pos2 != -1:
			s = s[:pos1] + s[pos2+2:]
	pos1 = s.find('/*')
	if pos1 != -1:
		s = s[:pos1]

        #去掉代码中的//注释
	s_lines = s.split('\n')
	s = ''
	for line in s_lines:
		pos = line.find("//")
		if pos != -1:
			line = line[:pos]
		s = s + ' ' +line
	
	s = s.replace('\n', '').replace('\t', '').replace('\r', '')
	s = s.replace('}', ' } ')
	s = s.replace('{', ' { ')
	s = s.replace('))', ') )')
	s = s.replace('))', ') )')   
	s = s.replace('))', ') )')   
	
	for ch in {'}','{','(',')',';','.','[',']','!','-','\'','\"','\\','*','<','>','@','~','#','$','%','&','^','+','=','?','_',',',':','/','|',','}:
		temp_str = ' ' + ch + ' '
		#s = s.replace(ch,temp_str)
		s = s.replace(ch,' ')	

	list1 = s.split()
	#s = ' '.join(list1)	
	
	list2 = []
	for i in range(len(list1)):
		list2 += resolve(list1[i])	
	


	wnl = WordNetLemmatizer()
	#delete stop words
	stopWords = GetListOfStopWords('/home/wdz/ENstopwords891.txt')
	#print stopWords 

	delStopList = []
	for word in list2:
		word = word.lower()
		#print word,
		word = wnl.lemmatize(word)
		#print word
 		if word not in stopWords:
			#print word
			delStopList.append(word)
	
	s = ' '.join(delStopList) 
	return s

def deal_comment(s):
	
	if  s.find('inheritDoc') != -1 or s.count('*') < s.count('\n'):
		return ""
	
        s = s.replace('\n', ' ')
        s = s.replace('/', ' ')
        s = s.replace('*', ' ')	
        s = s.replace('\"',' ')
        #modify1 s = s.replace('\'',' ') ’需要删除的情况很少，同时有类似map's存在
        #大部分@param都是多余的，
	
        #modify2 @param,@author 后面紧跟的字符通常无意义
        #s = s.replace('@param', ' ')
        s = re.sub(r'@param [a-zA-Z\. ]* ',' ',s)
        s = re.sub(r'@author [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@return [a-zA-Z\. ]* ',' ',s)
        s = re.sub(r'@throws [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@deprecated [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@see [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@since [a-zA-Z\. ]* ',' ',s)
	
        #modify4 找'.',而且不是表示引用的.如class.method
        pos = s.find('.')
        if pos != -1:
                while len(s) > pos+1 and s[pos+1].isalpha():
                        pos = s.find('.',pos+1)
                s = s[:pos]


        #modify5 处理 Class#method 的情况
        '''
        pos1 = s.find('#')
        while pos1 != -1:
                temp_s = re.sub(r'\w*#\w*',' ',s)
                #print temp_s
                s = temp_s
                #pattern = re.compile(r'\w+#\w+')
                #s = pattern.sub(' ', s)
			
                pos1 = s.find('#')
        '''

        
        #处理{@code something}的情况
        #处理后：something
        pos1 = s.find('{')
        while pos1 != -1:
                pos2 = s.find('}',pos1)
                if pos2 != -1:
                        mid_s = s[pos1:pos2+1]
                        pattern = re.compile(r'@\w+')
                        sub_s = pattern.sub(' ', mid_s)
                        sub_s = sub_s.replace('{', ' ')
                        sub_s = sub_s.replace('}', ' ')
                        s = s[:pos1] + sub_s + s[pos2+1:]
			
                        pos1 = s.find('{')
                else:
                        break
	#删除()及括号里面的内容
        s = remove(s,'(', ')')

	
	
        #modify6
        s = remove(s,'<', '>')
        '''
        for ch in {'}','{','(',')',';',':','.','[',']','!','-','\'','\"','<','>','@','~','#','%','^','&','*','+','+','?','_'}:
                s.replace(ch,' ')
        '''
        s = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）{}=;:!-<>`]+", " ",s)



        list1 = s.split()
	#s = ' '.join(list1)
	#print "list1= ",list1
	list2 = []
	for i in range(len(list1)):
		list2 += resolve(list1[i])	
	
	#delete stop words
	stopWords = GetListOfStopWords('/home/wdz/ENstopwords891.txt')
	
	delStopList = []
	for word in list2:
		word = word.lower()
 		if word not in stopWords:
			#print word
			delStopList.append(word)
	
	s = ' '.join(delStopList) 
	return s
	
def readdata(filename):

	file_train = "fasttext_tra" +  ".txt"
	file_test = "fasttext_tes" +  ".txt"
	f_train= open(file_train, 'a')
	f_test= open(file_test, 'a')
	fdata = io.open('P_'+filename, 'r',encoding='utf-8')

	done = 0
	count = 0
        ii = 0 
	while not done:
		Line = fdata.readline()
		if (Line != ''):
			one = {}
			if Line[0:4] == '#No.':
				
				IDpattern = re.compile(r'#No.(\d+)')
				fdata.readline()
				Line = fdata.readline()
			if Line[0:9] == '#Comment:':
				Line = fdata.readline()
				comment = Line
				done2 = 0
				while not done2:
					#print ii
					Line = fdata.readline()
					if Line.find('#Code') != -1:
						code = ''
						done3 = 0                     
						while not done3:
							Line = fdata.readline()
							if Line.find('#end') != -1:
								done3 = 1
								break
							else:
								pos = Line.find('//')                           
								if pos != -1:
									Line = Line[:pos]
								code = code + Line
						break
					else:
						#print "comment= ",comment
						comment = comment + Line
                                ii = ii +1
				#print ii
				one['Comment'] = comment
				one['Code'] = code
				#print comment,code
				#print comment 
				string_comment = deal_comment(one['Comment'])
				string_code = deal_code(remove_chinese(one['Code']))
				#print string_comment
				#print string_comment != ""
				#print string_code != ""
				if check_contain_chinese(one['Comment']) == False and string_comment != "" and string_code != "":
					count = count + 1 
					#print ii
					if count % 10 == 4:
						f_test.write( string_code + '       ')
					
						if filename[0:3] == 'neg':
							f_test.write( string_comment+ '\t__label__neg'+'\n')
						else:
							f_test.write( string_comment + '\t__label__pos'+'\n')
					else:
						f_train.write( string_code + '       ')
					
						if filename[0:3] == 'neg':
							f_train.write( string_comment + '\t__label__neg'+'\n')
						else:
							f_train.write( string_comment + '\t__label__pos'+'\n')
				#print ii 

		else:
			done = 1
	fdata.close()  
	f_train.close()
	f_test.close()
   
if __name__ == '__main__':
	#modify
	#readdata('P_neg.txt')
	
	argv = sys.argv
	mydic = getargvdic(argv)
	if '-tag' in mydic.keys():
		tag = mydic['-tag']
		readdata(tag)
	else:
		print "Please enter Tag with -tag. "

	
	
	
	
	
	
