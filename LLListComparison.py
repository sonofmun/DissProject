'''
Created on 30.04.2013
by Matthew Munson
The purpose of this script is to compare the log likelihood scores for every word with every other word in both Testaments.
So, e.g., it will look at θεος, see that it has a 3 LL score for a certain word in the LXX and a 1 LL for that word in the NT and will caculate the difference (2).
This will point out which words occur more in the context of the target word in each testament.  Positive score = more in LXX, negative = more in NT.
'''
import re
import pickle
import math
import os.path
import decimal
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
import decimal
def LLDict_Constructor(filename):
    #LemmaList = []
    #print(file)
    Lemma = re.sub(r'Coll_([^_]+)_[^.]+.txt', r'\1', file)
    #LemmaList.append(Lemma)
    LLFile = open(LLFilename, mode = 'r', encoding = 'utf-8') #opens the source file
    LLDictLemm = {}
    #LLDict_Complete = {}
    for line in LLFile:
        if 'Lemma' in line:
            continue
        else:
            LLDictLemms = re.sub(r'([^ ]+) [^ ]+ ([^\n]+)\n', r'\1', line)
            #print(LLDictLemms)
            LLDictVals = float(re.sub(r'([^ ]+) [^ ]+ ([^\n]+)\n', r'\2', line))
            if LLDictVals >= 0 or LLDictVals <= 0: # this puts the cutoff probability according to chi-squared at 99.9%
                LLDictLemm[LLDictLemms] = LLDictVals
    #LLDict_Complete[Lemma] = LLDictLemm
    LLFile.close()
    return LLDictLemm, Lemma
CollDir1 = askdirectory(title = 'In which directory are your source files for corpus 1 stored?')
FileList1 = os.listdir(CollDir1) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
CollDir2 = askdirectory(title = 'In which directory are your source files for corpus 2 stored?', initialdir = CollDir1)
FileList2 = os.listdir(CollDir2) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
DestDir = askdirectory(title = 'In which directory would you like to store the resulting similarity lists?', initialdir = CollDir1)
#DestFile = asksaveasfilename(title = 'Choose the directory and the filename for your results file', initialdir = CollDir1)
#The following loop creates the LLDict that contains the collocates and LL values for every lemma.
#It has the form, e.g., {'θεός':{'κύριος':75.8554929234818, ἐγώ:20.2976784605015...
#Doing this here means I won't have to create the dictionaries for each word multiple times.
LLDict_Complete1 = {}
LemmaList1 = []
LLDict_Complete2 = {}
LemmaList2 = []
for file in FileList1:
    #LemmaList = []
    #LLDict_Complete = {}
    LLFilename = CollDir1 + '/' + file #sets the absolute path for the source file
    if os.path.isfile(LLFilename) is True:
        LLDict_Add1, Lemma_Add1 = LLDict_Constructor(file)
    #if LLDict_Add1 and Lemma_Add1:
        LemmaList1.append(Lemma_Add1)
        LLDict_Complete1[Lemma_Add1] = LLDict_Add1
for file in FileList2:
    #LemmaList = []
    #LLDict_Complete = {}
    LLFilename = CollDir2 + '/' + file #sets the absolute path for the source file
    if os.path.isfile(LLFilename) is True:
        LLDict_Add2, Lemma_Add2 = LLDict_Constructor(file)
    #if LLDict_Add2 and Lemma_Add2:
        LemmaList2.append(Lemma_Add2)
        LLDict_Complete2[Lemma_Add2] = LLDict_Add2
LemListIntersection = set(LemmaList1).intersection(set(LemmaList2))
for Lemma in LemListIntersection:
    LLDiffDict={}
    #CosSimGroup = {}
    LLDict1 = LLDict_Complete1[Lemma]
    LLDict2 = LLDict_Complete2[Lemma]
    #CosSimFileName = Lemma + '_CosSim.txt' #sets the name of the destination file 
    #CosSimFilePath = DestDir + '/' + CosSimFileName #sets the absolute path for the destination file
    #CosSim = LLListComparison(LLDict1, LLDict2)
    for lem in LLDict1:
        if lem in LLDict1 and lem in LLDict2:
            LLDiffDict[lem] = LLDict1[lem] - LLDict2[lem]
    LLDiffDictStr = str(LLDiffDict).strip('{}').replace(', ', '\n').replace(': ', ',').replace("'", "")
    DestFile = DestDir + "/" + Lemma + "_LLDiff.txt"
    LLDiffFile = open(DestFile, mode = 'w', encoding = 'utf-8')
    LLDiffFile.write(LLDiffDictStr)
    LLDiffFile.close()
