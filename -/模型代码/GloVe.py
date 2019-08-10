# -*- coding: utf-8 -*- 
import re
import sys
from nltk.stem import WordNetLemmatizer
reload(sys)
sys.setdefaultencoding('utf-8')
import random
import imp  
import numpy as np
import io
import codecs, json 
from keras.models import * 
from keras.layers import * 
from keras.applications import * 
from keras.preprocessing.image import *
imp.reload(sys)  

texts = []
label = []
word_index = {}
res = dict()
chunk_size = 100

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
	stopWords = GetListOfStopWords('/home/wdz/ENstopwords891.txt')
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
	#s = s.replace('\n', ' ')//等待@param等处理完成
        s = s.replace('/', ' ')
        s = s.replace('*', ' ')	
        s = s.replace('\"',' ')

        s = re.sub(r'@author [a-zA-Z\. ]* ',' ',s)
	#s = re.sub(r'@return [a-zA-Z\. ]* ',' ',s)
        s = re.sub(r'@throws [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@deprecated [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@see [a-zA-Z\. ]* ',' ',s)
	s = re.sub(r'@since [a-zA-Z\. ]* ',' ',s)
	
	
	#solve @param
	c = re.sub(r'@SuppressWarnings.*',' ',c)

	left_index = int(c.find('('))
	right_index = int(c.find(')'))
	if(left_index + 1 != right_index):
		param_code_list = get_param_in_code(c,left_index,right_index,index)
		param_comment_list = get_param_in_comment(s)
		
		if(is_param_coherence(param_comment_list,param_code_list,index) == 0):
			s ="incoherencetype"
	
	s = re.sub(r'@param [a-zA-Z\. ]* ',' ',s)	
	
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
	
	delete_words_list = delete_stop_words(list_resolve)
	#print(len(delete_words_list))
	s = ' '.join(delete_words_list) 

	return delete_words_list

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
def process_code(s,index):

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
	delete_words_list = delete_stop_words(list_resolve)
	
	#print delete_words_list
	#print(len(delete_words_list))
	s = ' '.join(delete_words_list) 

	return delete_words_list
def GetListOfStopWords(filepath):
    f_stop = open(filepath)
    try:
        f_stop_text = f_stop.read().replace('\r','')
        f_stop_text = unicode(f_stop_text, 'utf-8').encode('utf-8')
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
		comment_list =[]
		comment_list = process_comment(comment,code,index)
		
		#process_code
		code_list = []
		code_list =  process_code(code,index)
		
		comment  = ' '.join(comment_list) 
		code = ' '.join(code_list) 

		if check_contain_chinese(comment) == False  and len(code_list) != 0 and len(comment_list) !=0:
			count = random.randint(0,9)

			texts.append(comment+'       '+code)
			label.append(res[index])
			texts.append(code+'       '+comment)
			label.append(res[index])
			if count <= 1:
				f_test.write( comment + '###')
					
				if res[index] == 0:
					f_test.write( code+ '\t__label__neg'+'\n')
				else:
					f_test.write( code + '\t__label__pos'+'\n')

				f_test.write( code + '###')
					
				if res[index] == 0:
					f_test.write( comment+ '\t__label__neg'+'\n')
				else:
					f_test.write( comment + '\t__label__pos'+'\n')
			else:
				f_train.write( comment + '###')
					
				if res[index] == 0:
					f_train.write( code + '\t__label__neg'+'\n')
				else:
					f_train.write( code + '\t__label__pos'+'\n')

				f_train.write( code + '###')
					
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

###############读取词向量 
def buildModel():
	embeddings_index = {} 
	f = io.open('glove.6B.50d.txt','r',encoding='utf-8') 
	for line in f.readlines(): 
		values = line.split() 
		word = values[0] 
		coefs = np.asarray(values[1:], dtype='float32') 
		embeddings_index[word] = coefs 
	f.close() 

	#return embeddings_index
	#print('Found %s word vectors.' % len(embeddings_index))


	#############我们可以根据得到的字典生成上文所定义的词向量矩阵 
	from keras.preprocessing.text import Tokenizer 
	from keras.preprocessing.sequence import pad_sequences 
	tokenizer = Tokenizer() 
	tokenizer.fit_on_texts(texts) 
	sequences = tokenizer.texts_to_sequences(texts) 
	
	word_index = tokenizer.word_index

	data = pad_sequences(sequences,chunk_size) 
	# from keras.utils import np_utils 
	# labels = np_utils.to_categorical(np.asarray(labels)) 
	#print('Shape of data tensor:', data.shape)
	#print data

	# split the data into a training set and a validation set 
	#print data.shape[0]
	indices = np.arange(data.shape[0]) 
	np.random.shuffle(indices) 
	data = data[indices] 
	labels_new = [] 
	for i in indices: 
		labels_new.append(label[i])
	
	nb_validation_samples = int(0.2 * data.shape[0]) 
	x_train = data[:-nb_validation_samples] 
	y_train = labels_new[:-nb_validation_samples] 
	x_val = data[-nb_validation_samples:] 
	y_val = labels_new[-nb_validation_samples:] 
	#print(x_train[0])

	#print word_index
	#中间先用glove能表示的多个符号隔开，测试说明。
	embedding_matrix = np.zeros((len(word_index) + 1, 50)) 
	for word, i in word_index.items():
		embedding_vector = embeddings_index.get(word) 
		if embedding_vector is not None: 
			# words not found in embedding index will be all-zeros. 
			embedding_matrix[i] = embedding_vector 

	#print embedding_matrix
	#print len(embedding_matrix.tolist())
	#embedding_matrix_json = json.dumps(embedding_matrix.tolist())
	#json.dump(embedding_matrix_json, codecs.open('embedding_matrix.txt', 'w', encoding='utf-8'))

	#########我们将这个词向量矩阵加载到Embedding层中，注意，我们设置trainable=False使得这个编码层不可再训练。
	from keras.layers import Embedding 
	#10036？搜索一下
	embedding_layer = Embedding(len(word_index) + 1, 50, weights=[embedding_matrix], input_length=chunk_size, trainable=False)


	sequence_input = Input(shape=(chunk_size,), dtype='int32') 
	embedded_sequences = embedding_layer(sequence_input) 

	x = Conv1D(64, 3, activation='relu')(embedded_sequences) 
	x = Conv1D(64, 3, activation='relu')(x) 
	x = MaxPooling1D(3)(x) 
	x = Conv1D(128, 3, activation='relu')(x) 
	x = Conv1D(128, 3, activation='relu')(x) 
	x = GlobalAveragePooling1D()(x) 
	x = Dropout(0.5)(x)

	preds = Dense(1, activation='sigmoid')(x) 
	
	'''
	LSTM
	x = LSTM(128)(embedded_sequences)
	x = Dropout(0.5)(x)
	'''
	'''
	x = Conv1D(128, 5, activation='relu')(embedded_sequences) 
	x = MaxPooling1D(5)(x) 
	x = Conv1D(128, 5, activation='relu')(x) 
	x = MaxPooling1D(5)(x) 
	#x = Conv1D(128, 5, activation='relu')(x) 
	#x = MaxPooling1D(35)(x) 

	# global max pooling 
	x = Flatten()(x) 
	x = Dense(128, activation='relu')(x) 
	preds = Dense(1, activation='sigmoid')(x) 
	'''
	model = Model(sequence_input, preds) 
	model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['acc']) 
	# happy learning! 
	model.fit(x_train, y_train, validation_data=(x_val, y_val), nb_epoch=200, batch_size=128) 
	model.save('mymodel.h5')

	model.summary()
if __name__ == '__main__':
	
	builddict()
	
	argv = sys.argv

	readdata()

	buildModel()
	#embedding_matrix = getWordEmbedding_existing()
	
'''
	mydic = getargvdic(argv)
	if '-tag' in mydic.keys():
		tag = mydic['-tag']
		readdata(tag)
	else:
		print "Please enter Tag with -tag. "
'''


