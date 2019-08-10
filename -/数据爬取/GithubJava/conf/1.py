for i in range(100, 1200, 50):
    ConfFile = open(str(i) + 'TO' + str(i + 50), 'w')
    ConfFile.write('0\n'+ str(i) +'\n1')



