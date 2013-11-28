'''
Created on 30.04.2013
by Matthew Munson
The purpose of this file is to run a cosine similarity comparison between the collocation lists for every word that occurs in both the NT and LXX.
The resulting file will be a csv file where the first element of every line is the lemma and the second the similarity score of the collocation list in the LXX and the NT.
It will have the form "κύριος',.568\nσωτήρ:.523\n..."
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
def NP4LL_cosine_similarity(c1, c2):
    terms = set(c1).union(c2) #this produces a union set that contains all of the values in both dictionary 1 (c1) and dictionary 2 (c2)
    #the numerator for the cosine similarity.  
    #Iterates over the terms in 'terms' and returns the LL value in c1 and c2.
    #Returns 0 if the term does not exist in the dictionary.
    dotprod = sum(c1.get(k, 0) * c2.get(k, 0) for k in terms) 
    #returns the sqrt of sums of the squared values for all terms in c1 and c2.
    magA = math.sqrt(sum(c1.get(k, 0)**2 for k in terms))
    magB = math.sqrt(sum(c2.get(k, 0)**2 for k in terms))
    #returns the cosine similarity of the two dictionaries
    if magA != 0 and magB != 0:
        return dotprod / (magA * magB) 
    else:
        return 0
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
            LLDictLemms = re.sub(r'([^ ]+) [^ ]+ ([^\n]+)[\n]?', r'\1', line)
            #print(LLDictLemms)
            LLDictVals = float(re.sub(r'([^ ]+) [^ ]+ ([^\n]+)[\n]?', r'\2', line))
            if LLDictVals >= 0.455 or LLDictVals <= -0.455: # this puts the cutoff probability according to chi-squared at 50%
                LLDictLemm[LLDictLemms] = LLDictVals
    #LLDict_Complete[Lemma] = LLDictLemm
    LLFile.close()
    return LLDictLemm, Lemma
CollDir1 = askdirectory(title = 'In which directory are your collocation lists for corpus 1 stored?')
FileList1 = os.listdir(CollDir1) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
LemFileName1 = askopenfilename(title = 'Which file contains your lemmas for corpus 1?')
LemFile1 = open(LemFileName1, mode = 'r', encoding = 'utf-8')
CollDir2 = askdirectory(title = 'In which directory are your collocation lists for corpus 2 stored?', initialdir = CollDir1)
FileList2 = os.listdir(CollDir2) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
LemFileName2 = askopenfilename(title = 'Which file contains your lemmas for corpus 2?')
LemFile2 = open(LemFileName2, mode = 'r', encoding = 'utf-8')
#DestDir = askdirectory(title = 'In which directory would you like to store the resulting similarity lists?', initialdir = CollDir1)
DestFile = asksaveasfilename(title = 'Choose the directory and the filename for your results file', initialdir = CollDir1)
#The following loop creates the LLDict that contains the collocates and LL values for every lemma.
#It has the form, e.g., {'θεός':{'κύριος':75.8554929234818, ἐγώ:20.2976784605015...
#Doing this here means I won't have to create the dictionaries for each word multiple times.
LLDict_Complete1 = {}
LemmaList1 = []
LLDict_Complete2 = {}
LemmaList2 = []
Lemmas1 = LemFile1.read().strip("'").splitlines()
Lemmas2 = LemFile2.read().strip("'").splitlines()
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
CSDict={}
for Lemma in LemListIntersection:
    #CosSimGroup = {}
    LLDict1 = LLDict_Complete1[Lemma]
    LLDict2 = LLDict_Complete2[Lemma]
    #CosSimFileName = Lemma + '_CosSim.txt' #sets the name of the destination file 
    #CosSimFilePath = DestDir + '/' + CosSimFileName #sets the absolute path for the destination file
    CosSim = NP4LL_cosine_similarity(LLDict1, LLDict2)
    CSDict[Lemma] = str(CosSim) + ',' + str(Lemmas1.count(Lemma)) + ',' + str(Lemmas2.count(Lemma))
CSDictStr = str(CSDict).strip('{}').replace(', ', '\n').replace(': ', ',').replace("'", "")
CosSimFile = open(DestFile, mode = 'w', encoding = 'utf-8')
CosSimFile.write(CSDictStr)
CosSimFile.close()
'''
for file in FileList:
    LLFilename = CollDir + '/' + file #sets the absolute path for the source file
    if os.path.isfile(LLFilename) is True:
        Lemma = re.sub(r'Coll_([^_]+)_[^.]+.txt', r'\1', file)
        LLDict1 = LLDict_Complete[Lemma]
        LLFile = open(LLFilename, mode = 'r', encoding = 'utf-8') #opens the source file
        CosSimFileName = Lemma + '_CosSim.txt' #sets the name of the destination file 
        CosSimFilePath = DestDir + '/' + CosSimFileName #sets the absolute path for the destination file
        if os.path.isfile(CosSimFilePath) == True: #checks to see if a destination file already exists for this lemma
            continue #if a destination file for this lemma exists, it breaks out of the if loop and selects the next member of FileList
        else: #this triggers if the destination file does not yet exist
            CosSimGroup = {}
            for lem in LemmaList:
                if lem == Lemma:
                    continue
                else:
                    LLDict2 = LLDict_Complete[lem]
                    if LLDict1 != {} and LLDict2 != {}:
                        CosSim = NP4LL_cosine_similarity(LLDict1, LLDict2)
                        CosSimGroup[lem] = CosSim
        CSDict={}
        CSDict[Lemma] = CosSimGroup
        CSDictStr1 = str(list(dict.keys(CSDict)))
        CSDictStr2 = str(list(dict.items(CSDict[Lemma])))
        CSDictStr1 = CSDictStr1.strip('[]') + ',Lemma\n'
        CSDictStr2 = CSDictStr2.strip('[()]')
        CSDictStr2 = CSDictStr2.replace('), (', '\n')
        CSDictStr2 = CSDictStr2.replace(', ', ',')
        CSDictStr = CSDictStr1 + CSDictStr2
        CosSimFile = open(CosSimFilePath, mode = 'w', encoding = 'utf-8')
        CosSimFile.write(CSDictStr)
        CosSimFile.close()
        LLFile.close()
'''