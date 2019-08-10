for i in range(10, 100, 10):
    ConfFile = open(str(i) + 'TO' + str(i + 10), 'w')
    ConfFile.write('0\n'+ str(i) +'\n1')

for i in range(100, 1200, 100):
    ConfFile = open(str(i) + 'TO' + str(i + 100), 'w')
    ConfFile.write('0\n'+ str(i) +'\n1')



