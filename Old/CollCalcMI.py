'''
Created on 14.02.2013

@author: matthew.munson
'''
import re
import pickle
import os
import math
import os.path
lemdoc = open("C:/CompLing/GBible/XML/LemLists/GBibleLemmsLXX.txt", mode = 'rb')
lemlist = pickle.load(lemdoc)
FileList = os.listdir("C:/CompLing/GBible/XML/CollLists/LXX")
LemCount = 0
for file in FileList:    
    MICollList = []
    CollFilename = "C:/CompLing/GBible/XML/CollLists/LXX/" + file
    CollFile = open(CollFilename, mode = 'r', encoding = 'utf-8')
    MIfile = re.sub(r'.txt', r'_MI.txt', file)
    MIFileName = "C:/CompLing/GBible/XML/CollLists/LXX/MI/" + MIfile
    if os.path.isfile(MIFileName) == True: #checks to see if a collocation file already exists for this lemma
        continue #if a collocation file for this lemma exists, it breaks out of the if loop and selects the next member of lemlist
    else:
        MIListFile = open(MIFileName, mode = 'w', encoding = 'utf-8')
        for line in CollFile:
            if 'P=Lemma' in line:
                LemCount = int(re.sub(r'.+?Lemma W=[^\']+\', ([0-9]+).*\n', r'\1', line))
            if '(' in line:
                line = line.strip(',"\n') # = re.sub(r'\"', '', line, count = 1)
                LineList = re.split(r'\",+\"', line)
                for collocate in LineList:
                    if re.match('\",+\"', collocate):
                        continue
                    elif 'Lemma' in collocate:
                        MILem = re.sub(r'\"{,1}\(\'(P=Lemma) (W=[^\']+)\', ([0-9]+)\)\"{,1}', r'(\1 \2 N=\3 MI=NA', collocate)
                        MILem = MILem + ')'
                        MICollList.append(MILem)
                        continue
                    else:
                        CollCount = int(re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=[^\']+\', ([0-9]+)\)\"{,1}', r'\1', collocate))
                        CollLemCount = lemlist.count(re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=([^\']+)\', [0-9]+\)\"{,1}', r'\1', collocate))
                        Num = len(lemlist)
                        #Below is the PMI equation from Manning & Schütze, Foundations of Statistical NLP, 1999.
                        #It differs from what we see on http://linglit194.linglit.tu-darmstadt.de/linguisticsweb/bin/view/LinguisticsWeb/CollocationAnalysis
                        #The latter multiplies the numerator by N, which would produce answers N times larger than the former.
                        MI = math.log((CollCount/Num)/((LemCount/Num)*(CollLemCount/Num)), 2)
                        MIColl = re.sub(r'\"{,1}\(\'(P=[LR][0-9]{1,2}) (W=[^\']+)\', ([0-9]+)\)\"{,1}', r'(\1 \2 N=\3 MI=', collocate)
                        MIColl = MIColl + str(MI) + ')'
                        MICollList.append(MIColl)
        MICollStr = str(MICollList)
        MIListFile.write(MICollStr)
        MIListFile.close()
lemdoc.close()