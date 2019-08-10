# -*- coding: utf-8 -*- 
import re
import sys
import importlib
importlib.reload(sys)
from nltk.stem import WordNetLemmatizer
import random
import io

res = dict()

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
def resolve_list(s):

	def resolve(check_str):
		list_resolve = []
		tag1 = -1
		tag2 = -1
		index = 0
		for i in range(len(check_str)):
		
			tag2 = tag1

			if str(check_str[i]).islower():
				tag1 = 1
			elif str(check_str[i]).isupper():
				tag1 = 2
			elif str(check_str[i]).isdigit():
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
	
	list1 = s.split()

	list2 = []
	for i in range(len(list1)):
		list2 += resolve(list1[i].encode('utf-8'))

	return list2

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
def is_param_coherence(param_comment_list,param_code_list,index):
	num_of_0 = 0
	num_of_1 = 0
	for word in param_comment_list:
	
		res = 0
		for param in param_code_list:
			if(param.find(word)!=-1):
				res = 1
				num_of_1 = num_of_1 +1
				break
		if res == 0:
			num_of_0 = num_of_0 + 1
	
	if (num_of_1 >= (num_of_1+num_of_0)*0.8):
		return 1
	else:
		return 0

def get_param_in_code(c,left_index,right_index,index):

	temp_string = c[left_index+1:right_index]
	temp_string = temp_string.replace(',',' ')
	temp_string = temp_string.replace('\n',' ')

	paramlist1 = temp_string.strip().split() 

	paramlist = [] 
	for i in range(len(paramlist1)):
		paramlist.append(paramlist1[i].encode('utf-8').lower())
	
	return paramlist

def get_param_in_comment(s):
	wordlist = []
	loc1 = s.find('@param')
	if (loc1 != -1):
		loc2 = s.find('\n',loc1)
		word1 = s[loc1+7:loc2].split(' ')[0]
		wordlist.append(word1.encode('utf-8').lower())
	
		while(s.find('@param',loc1+1)!=-1):
			loc1 = s.find('@param',loc1+1)
			loc2 = s.find('\n',loc1)
			word1 = s[loc1+7:loc2].split(' ')[0]
			wordlist.append(word1.encode('utf-8').lower())
	
	return wordlist

def get_return_in_code(c):
	return_list = []
	left_index = int(c.find('('))
	first_index = c.rfind(' ',0,left_index)
	second_index = c.rfind(' ',0,first_index-1)
	return_list.append(c[second_index+1:first_index].encode('utf-8').lower())
	
	last_return = c[c.rfind(' ')+1:].encode('utf-8').lower()
	last_return = re.sub(r'[^a-z]',' ',last_return)
	last_return_list = last_return.strip().split(' ')
	#print last_return_list
	return_list.extend(last_return_list)

	return return_list
	
def is_return_coherence(return_comment,return_code_list,index):
	
	for param in return_code_list:
		if param.find(return_comment) != -1:
			return 1
	return 0

def first_line(s):
	pos = s.find('.')
	if pos != -1:
		while len(s) > pos+1 and s[pos+1].isalpha():
			pos = s.find('.',pos+1)
		s = s[:pos]

	return s
#处理{@code something}的情况
#处理后：something
def solve_code_something(s):
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
	
	return s
def delete_stop_words(list_resolve):
	stopWords = GetListOfStopWords('ENstopwords891.txt')
	wnl = WordNetLemmatizer()

	delStopList = []
	for word in list_resolve:
		word = word.lower()
		word = wnl.lemmatize(word)

		if word not in stopWords:
			#print word
			delStopList.append(word.encode('utf-8'))
	
	return delStopList
	
def process_comment(s,c,index):

	s = s.replace('/', ' ')
	s = s.replace('*', ' ')
	s = s.replace('\"',' ')
	s = re.sub(r'@author[a-zA-Z\. ]* ',' ',s)
	#s = re.sub(r'@return [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@throws[a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@deprecated[a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@see[a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@since[a-zA-Z\. ]* ',' ',s)
	


	c = re.sub(r'@SuppressWarnings.*',' ',c)

	left_index = int(c.find('('))
	right_index = int(c.find(')'))
	if(left_index + 1 != right_index):
		param_code_list = get_param_in_code(c,left_index,right_index,index)
		param_comment_list = get_param_in_comment(s)
		
		if(is_param_coherence(param_comment_list,param_code_list,index) == 0):
			s ="incoherencetype"
	
	s = re.sub(r'@param[a-zA-Z\. ]* ',' ',s)
	
	'''
	#solve @return
	loc1 = s.find('@return')
	if(loc1 != -1):
		loc2 = s.find('\n',loc1)
		word_list = s[loc1+8:loc2].split(' ')
		if(len(word_list) > 1):
			s = s.replace('@return','return')
		else:
			word_list[0] = re.sub(r'[^a-zA-Z]','',word_list[0])
			return_comment = word_list[0].encode('utf-8').lower()
			return_code_list = get_return_in_code(c)
			if(is_return_coherence(return_comment,return_code_list,index) == 0):
				s ="incoherencetype"
			
			s = re.sub(r'@return [a-zA-Z\. ]* ',' ',s)
	'''
	
	############
	s = first_line(s)
	#solve {#code }	
	s = solve_code_something(s)
	
	s = remove(s,'(', ')')

	s = remove(s,'<', '>')
	
	s = re.sub(r'[^a-zA-Z]',' ',s)

	list_resolve = resolve_list(s)
	
	#delete_words_list = delete_stop_words(list_resolve)
	#print(len(delete_words_list))
	#s = ' '.join(delete_words_list)

	file_comment = "middle_comment.txt"
	f_comment = open(file_comment,'a')
	f_comment.write(s)
	f_comment.write("\n\n\n")
	f_comment.close()
	return s

def remove_comment(s):
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
	
	return s
def process_code(s):

	if s.find('class')!= -1 or s.find('enum')!=-1 or s.find('interface')!=-1 or s.count('private')+s.count('public') >= 2:
		return ""
	
	s = re.sub(r'@SuppressWarnings.* ',' ',s)

	#s = remove_comment(s)
	
	#s = re.sub(r'[^a-zA-Z]',' ',s)
	
	s = re.sub(r'[^a-zA-Z{};]',' ',s)
	s = s.replace('}', ' } ')
	s = s.replace('{', ' { ')
	s = s.replace(';', ' ; ')
	'''
	s = s.replace('))', ') )')
	s = s.replace('))', ') )')   
	s = s.replace('))', ') )')  
	'''
	
	list_resolve = resolve_list(s)
	#print list_resolve
	#delete_words_list = delete_stop_words(list_resolve)
	#print delete_words_list
	#print(len(delete_words_list))
	s = ' '.join(list_resolve)

	file_code = "middle_code.txt"
	f_code = open(file_code,'a')
	f_code.write(s)
	f_code.write("\n\n\n")
	f_code.close()
	return s

def GetListOfStopWords(filepath):
	f_stop = open(filepath)
	try:
		f_stop_text = f_stop.read().replace('\r','')
	finally:
		f_stop.close()
	f_stop_seg_list = f_stop_text.split('\n')

	return f_stop_seg_list

def readdata():

	file_train = "fasttext_tra" +  ".txt"
	file_test = "fasttext_tes" +  ".txt"
	f_train= open(file_train, 'w')
	f_test= open(file_test, 'w')
	f_data = io.open("Benchmark_Raw_Data.txt", 'r',encoding='utf-8')
	
	while(1):
		line = f_data.readline()
		if(line == ""):
			break

		templist = line.strip().split(', ')
	
		index = int(templist[0])
		nameofmethod = templist[1]
		filepath_line = f_data.readline()

		num_of_comment = f_data.readline()
		num = int(num_of_comment)
		comment = ""
		for i in range(0,num):
			line = f_data.readline()
			comment += line

		num_of_code = f_data.readline()
		num_code = int(num_of_code)
		code = ""
		for i in range(0,num_code):
			line = f_data.readline()
			code += line
	
		#process_comment
		comment = process_comment(comment,code,index)
		
		#process_code
		code = process_code(code)
		
		if check_contain_chinese(comment) == False  and code != "":
			count = random.randint(0,9)
			
			if count <= 1:
				f_test.write( code + '       ')
					
				if res[index] == 0:
					f_test.write( comment+ '\t__label__neg'+'\n')
				else:
					f_test.write( comment + '\t__label__pos'+'\n')
			else:
				f_train.write( code + '       ')
					
				if res[index] == 0:
					f_train.write( comment + '\t__label__neg'+'\n')
				else:
					f_train.write( comment + '\t__label__pos'+'\n')

		nouse_line = f_data.readline()

	f_train.close()
	f_test.close()
	f_data.close()

	text1 = GetListOfStopWords('fasttext_tes.txt')
	f_shuffle_test = open('test.txt','w')

	ran = random.random
	random.seed()

	random.shuffle(text1,ran)
	testText = '\n'.join(text1)
	testText.replace('\n\n','\n')
	f_shuffle_test.write(testText)
	f_shuffle_test.close()

	text2 = GetListOfStopWords('fasttext_tra.txt')
	f_shuffle_train = open('train.txt','w')
	random.shuffle(text2,ran)
	trainText = '\n'.join(text2)
	trainText.replace('\n\n','\n')
	f_shuffle_train.write(trainText)
	f_shuffle_train.close()
	
def builddict():
	file_open = "Benchmark_Coherence_Data.txt"
	f_data = open(file_open,'r')
	list_of_all_the_lines = f_data.readlines( )
	for line in list_of_all_the_lines:
		temp_list = line.strip().split(', ')
		#print temp_list
		num = int(temp_list[0])
		ans = int(len(temp_list[1]) < 8+1)
		res[num] = ans
		#print (num,ans)
	f_data.close()

if __name__ == '__main__':
	
	builddict()
	argv = sys.argv

	readdata()
'''
	mydic = getargvdic(argv)
	if '-tag' in mydic.keys():
		tag = mydic['-tag']
		readdata(tag)
	else:
		print "Please enter Tag with -tag. "
'''
