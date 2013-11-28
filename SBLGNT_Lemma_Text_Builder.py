'''
Created on 11.04.2013
This file takes as its input the list of txt files from the SBLGNT Github repository, extracts the lemmata from each of the files, and creates a new
txt file that contains just an ordered list object of lemmata.
@author: matthew.munson
'''
import re
import os
import pickle
FileList = os.listdir("C:/CompLing/GBible/SBLGNT/sblgnt-master")
LemmaOut = open("C:/CompLing/GBible/SBLGNT/sblgnt-master/SBLGNTLemmas.txt", mode='w', encoding = 'utf-8')
AllLemmas = '' #[]
for file in FileList:
    if '.txt' in file:
        InputFilename = 'C:/CompLing/GBible/SBLGNT/sblgnt-master/' + file
        InputFile = open(InputFilename, mode='r', encoding='utf-8')
        for line in InputFile:
            line = line.strip('\n')
            Lemma = re.sub(r'[\S]+ [\S]+ [\S]+ [\S]+ [\S]+ [\S]+ ([\S]+)', r'\1', line)
#            print(Lemma)
            AllLemmas = AllLemmas + Lemma + '\n'#.append(Lemma) 
        InputFile.close()
LemmaOut.write(AllLemmas)
#pickle.dump(AllLemmas, LemmaOut)
LemmaOut.close()
