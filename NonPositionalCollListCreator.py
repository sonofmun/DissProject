'''
Created on 07.03.2013

@author: matthew.munson
'''
import re
import os.path
from tkinter.filedialog import askdirectory
CollDir = askdirectory(title = 'In which directory are your collocation lists stored?')
FileList = os.listdir(CollDir)
LemCount = 0
for file in FileList:    
    NPCollList = {}
    CollFilename = CollDir + "/" + file
    with open(CollFilename, mode = 'r', encoding = 'utf-8') as CollFile:        
        LLfile = re.sub(r'.txt', r'_NP4.txt', file)
        NPFileName = CollDir + "/NP4/" + LLfile
        if os.path.isfile(NPFileName) == True: #checks to see if a collocation file already exists for this lemma
            continue #if a collocation file for this lemma exists, it breaks out of the if loop and selects the next member of lemlist
        else:
            NPListFile = open(NPFileName, mode = 'w', encoding = 'utf-8')
            for line in CollFile:
                if 'P=Lemma' in line:
                    LemWord = re.sub(r'.+?Lemma W=([^\']+)\', [0-9]+.*\n', r'\1', line)
                    LemCount = int(re.sub(r'.+?Lemma W=[^\']+\', ([0-9]+).*\n', r'\1', line))
                    LemKey = 'Lemma(' + LemWord + ')'
                    NPCollList.setdefault(LemKey, LemCount)                
        #        CollIndex = 0
                if '(' in line:
                    line = line.strip(',"\n') # = re.sub(r'\"', '', line, count = 1)
                    LineList = re.split(r'\",+\"', line)
                    for collocate in LineList:
                        if re.match('\",+\"', collocate):
                            continue
                        elif 'Lemma' in collocate:
                            continue
                        elif int(re.sub(r'\"{,1}\(\'P=[LR]([0-9]{1,2}) W=[^\']+\', [0-9]+\)\"{,1}', r'\1', collocate)) > 4:
                            continue
                        else:
        #                    print(collocate)
                            CollWord = re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=([^\']+)\', [0-9]+\)\"{,1}', r'\1', collocate)
                            CollCount = int(re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=[^\']+\', ([0-9]+)\)\"{,1}', r'\1', collocate))
                            if CollWord not in NPCollList:
                                NPCollList.setdefault(CollWord, CollCount)
                            else:
                                TotCollCount = NPCollList[CollWord] + CollCount
                                NPCollList[CollWord] = TotCollCount
            NPCollStr = str(NPCollList)
            NPCollStr = re.sub(r'[\{\}:]', '', NPCollStr)
            NPCollStr = re.sub(r', ', r'\n', NPCollStr)
            NPListFile.write(NPCollStr)
            NPListFile.close()
