import random

def GetListOfStopWords(filepath):
    f_stop = open(filepath)
    try:
        f_stop_text = f_stop.read().replace('\r','')
        f_stop_text = unicode(f_stop_text, 'utf-8').encode('utf-8')
    finally:
        f_stop.close()
    f_stop_seg_list = f_stop_text.split('\n')

    return f_stop_seg_list


if __name__ == '__main__':
	#modify
	
	text1 = GetListOfStopWords('fasttext_tes.txt')
	f_test = open('test.txt','w')

	ran = random.random
	random.seed()

	random.shuffle(text1,ran)
	testText = '\n'.join(text1)
	testText.replace('\n\n','\n')
	f_test.write(testText)
	f_test.close()

	text2 = GetListOfStopWords('fasttext_tra.txt')
	f_train = open('train.txt','w')
	random.shuffle(text2,ran)
	trainText = '\n'.join(text2)
	trainText.replace('\n\n','\n')
	f_train.write(trainText)
	f_train.close()
