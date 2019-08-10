# _*_coding:utf-8 _*_
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import fasttext
import sys
import getopt,optparse
import os

def getargvdic(argv):
	optd = {}
	while argv:
		if argv[0][0] == '-':
			optd[argv[0]] =argv[1]
			argv = argv[2:]
		else:
			argv = argv[1:]
	return optd

if __name__ == '__main__':
	
	f = open('result_new.txt','w')
	f.write('----------------------------------------------------\n')
	
		
	
	argv = sys.argv
	mydic = getargvdic(argv)

	if '-lr' in mydic.keys():
		lr1 = int(mydic['-lr'])
		f.write('learn rate = %d' % (lr1) )
		f.write(lr1)
	else:
		lr1 = 0.1
		print('Default learn rate = 0.1')
	
	################

	if '-dim' in mydic.keys():
		dim1 = int(mydic['-dim'])
		f.write('dim = %d ' % (dim1) )
		print('dim = %d' % (dim1) )
	else:
		dim1 = 100
		print('Default dim = 100')

	if '-ws' in mydic.keys():
		ws1 = int(mydic['-ws'])
		f.write('ws = %d ' % (ws1) )
		print('ws = %d' % (ws1) )
	else:
		ws1 = 5
		print('Default ws = 5')

	if '-epoch' in mydic.keys():
		epoch1 = int(mydic['-epoch'])
		f.write('epoch = %d ' % (epoch1) )
		print('epoch = %d' % (epoch1) )
	else:
		epoch1 = 40
		print('Default epoch = 40')
	
	if '-min_count' in mydic.keys():
		min_count1 = int(mydic['-min_count'])
		f.write('min_count = %d ' % (min_count1) )
		print('min_count = %d' % (min_count1) )
	else:
		min_count1 = 1
		print('Default min_count = 1')

	if '-neg' in mydic.keys():
		neg1 = int(mydic['-neg'])
		f.write('neg = %d ' % (neg1) )
		print('neg = %d' % (neg1) )
	else:
		neg1 = 5
		print('Default neg = 5')



	#训练模型
	classifier = fasttext.supervised("train.txt","comment_code_fasttext.model",label_prefix="__label__",ws=ws1,lr=lr1,epoch=epoch1,dim=dim1,min_count=min_count1,neg=neg1)










