# -*- coding:utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import fasttext
from sklearn.metrics import roc_curve,auc 
import matplotlib.pyplot as plt 
#load训练好的模型
classifier = fasttext.load_model('comment_code_fasttext.model.bin', label_prefix='__label__')
result = classifier.test("test.txt")

print 
print "precision:",(result.precision)

print(result.recall)
labels_right = []
texts = []
with open("test.txt") as fr:
    lines = fr.readlines()
for line in lines:
    if line == '\n':
	continue
    labels_right.append(line.split("\t")[1].rstrip().replace("__label__","").encode('utf-8'))
    texts.append(line.split("\t")[0].decode("utf-8"))
#     print labels
#     print texts
#     break
labels_predict = [e[0].encode('utf-8') for e in classifier.predict(texts)] #预测输出结果为二维形式
# print labels_predict

text_labels = list(set(labels_right))
text_predict_labels = list(set(labels_predict))
#print text_predict_labels
#print text_labels
#print labels_right
#print labels_predict



A = dict.fromkeys(text_labels,0)  #预测正确的各个类的数目
B = dict.fromkeys(text_labels,0)   #测试数据集中各个类的数目
C = dict.fromkeys(text_predict_labels,0) #预测结果中各个类的数目

tp=0.0
fn=0.0
tn=0.0
fp=0.0

labels_scores = []

for i in range(0,len(labels_right)):
    B[labels_right[i]] += 1
    C[labels_predict[i]] += 1
    if labels_right[i] == labels_predict[i]:
        A[labels_right[i]] += 1
    if labels_right[i] == 'pos' and labels_predict[i] == 'pos':
	tp += 1
	labels_scores.append(1)
    if labels_right[i] == 'pos' and labels_predict[i] == 'neg':
	fn += 1
	labels_scores.append(0)
    if labels_right[i] == 'neg' and labels_predict[i] == 'neg':
	tn += 1
	labels_scores.append(0)
    if labels_right[i] == 'neg' and labels_predict[i] == 'pos':
	fp += 1
	labels_scores.append(1)

tpr = tp/(tp+fn)
fpr = fp/(fp+tn)

print A,
print "预测正确的各个类的数目"
print B,
print "测试数据集中各个类的数目"
print C,
print "预测结果中各个类的数目"
#计算准确率，召回率，F值
for key in B:
    p = float(A[key]) / float(B[key])
    r = float(A[key]) / float(C[key])
    f = p * r * 2 / (p + r)
    print "%s:\tp:%f\t%fr:\t%f" % (key,p,r,f)

print "----------------------------------------------------\n"
'''
fpr,tpr,threshold = roc_curve(labels_right, labels_scores,pos_label = 'pos')
roc_auc = auc(fpr,tpr)


plt.figure()  
lw = 2  
plt.figure(figsize=(10,10))  
plt.plot(fpr, tpr, color='darkorange',  
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc) ###假正率为横坐标，真正率为纵坐标做曲线  
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')  
plt.xlim([0.0, 1.0])  
plt.ylim([0.0, 1.05])  
plt.xlabel('False Positive Rate')  
plt.ylabel('True Positive Rate')  
plt.title('Receiver operating characteristic example')  
plt.legend(loc="lower right")  
plt.show()  

'''
