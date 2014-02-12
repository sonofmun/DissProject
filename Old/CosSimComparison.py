'''
Created on 30.04.2013
by Matthew Munson
The purpose of this script is to compare the cosine similarity scores for every word with every other word in both Testaments.
So, e.g., it will look at θεος, see that it has a .99 CS score for a certain word in the LXX and a .98 CS for that word in the NT and will caculate the difference (.01).
This will point out which words have more similar collocation fields in the LXX (Positive score) or the NT (negative score).
'''
import re
import pickle
import math
import os.path
import decimal
from tkinter.filedialog import asksaveasfilename
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import decimal
def CSDict_Constructor(filename):
    #LemmaList = []
    #print(file)
    #Lemma = re.sub(r'([^_]+)_[^.]+.txt', r'\1', file)
    #LemmaList.append(Lemma)
    with open(filename, mode = 'r', encoding = 'utf-8') as CSFile: #opens the source file
        CSDictLemm = {}
        #LLDict_Complete = {}
        for line in CSFile:
            if 'Lemma' in line:
                continue
            else:
                CSDictLemms = re.sub(r'([^,]+),([^\n]+)\n*', r'\1', line)
                #print(LLDictLemms)
                CSDictVals = float(re.sub(r'([^,]+),([^\n]+)\n*', r'\2', line))
                CSDictLemm[CSDictLemms] = CSDictVals
        #LLDict_Complete[Lemma] = LLDictLemm
    return CSDictLemm
CollDir1 = askdirectory(title = 'In which directory are your source files for corpus 1 stored?')
FileList1 = os.listdir(CollDir1) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
CollDir2 = askdirectory(title = 'In which directory are your source files for corpus 2 stored?', initialdir = CollDir1)
FileList2 = os.listdir(CollDir2) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
DestDir = askdirectory(title = 'In which directory would you like to store the resulting similarity lists?', initialdir = CollDir1)
#DestFile = asksaveasfilename(title = 'Choose the directory and the filename for your results file', initialdir = CollDir1)
#The following loop creates the LLDict that contains the collocates and LL values for every lemma.
#It has the form, e.g., {'θεός':{'κύριος':75.8554929234818, ἐγώ:20.2976784605015...
#Doing this here means I won't have to create the dictionaries for each word multiple times.
CSDict_Complete1 = {}
LemmaList1 = [re.sub(r'([^_]+)_[^.]+.txt', r'\1', file) for file in FileList1 if file.endswith('txt')]
CSDict_Complete2 = {}
LemmaList2 = [re.sub(r'([^_]+)_[^.]+.txt', r'\1', file) for file in FileList2 if file.endswith('txt')]
LemListIntersection = set(LemmaList1).intersection(set(LemmaList2))
for lemma in LemmaList1:
    if lemma in LemListIntersection:
        CSFilename = CollDir1 + '/' + lemma + '_CosSim.txt' #sets the absolute path for the source file
        if os.path.isfile(CSFilename) is True:
            CSDict_Add1 = CSDict_Constructor(CSFilename)
    #if LLDict_Add1 and Lemma_Add1:
            #LemmaList1.append(Lemma_Add1)
            CSDict_Complete1[lemma] = CSDict_Add1
for lemma in LemmaList2:
    if lemma in LemListIntersection:
        CSFilename = CollDir2 + '/' + lemma + '_CosSim.txt' #sets the absolute path for the source file
        if os.path.isfile(CSFilename) is True:
            CSDict_Add2 = CSDict_Constructor(CSFilename)
    #if LLDict_Add1 and Lemma_Add1:
            #LemmaList1.append(Lemma_Add1)
            CSDict_Complete2[lemma] = CSDict_Add2
for Lemma in LemListIntersection:
    CSDiffDict={}
    #CosSimGroup = {}
    try:
        CSDict1 = CSDict_Complete1[Lemma]
    except KeyError as E:
        continue
    try:
        CSDict2 = CSDict_Complete2[Lemma]
    except KeyError as E:
        continue
    #CosSimFileName = Lemma + '_CosSim.txt' #sets the name of the destination file 
    #CosSimFilePath = DestDir + '/' + CosSimFileName #sets the absolute path for the destination file
    #CosSim = LLListComparison(LLDict1, LLDict2)
    for lem in CSDict1:
        #if lem in CSDict1 and lem in CSDict2:
        CSDiffDict[lem] = [CSDict1.get(lem, 0), CSDict2.get(lem, 0),CSDict1.get(lem, 0) - CSDict2.get(lem, 0)]
    for lem in CSDict2:
        if lem not in CSDict1:
            CSDiffDict[lem] = [CSDict1.get(lem, 0), CSDict2.get(lem, 0),CSDict1.get(lem, 0) - CSDict2.get(lem, 0)]
    CSDiffDictStr = str(CSDiffDict).strip('{}').replace('[', '').replace('], ', '\n').replace(']', '').replace(': ', ',').replace("'", "")
    DestFile = DestDir + "/" + Lemma + "_CSDiff.txt"
    with open(DestFile, mode = 'w', encoding = 'utf-8') as CSDiffFile:
        CSDiffFile.write(CSDiffDictStr)
