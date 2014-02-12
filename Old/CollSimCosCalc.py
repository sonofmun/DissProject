'''
Created on 25.04.2013
by Matthew Munson
The purpose of this file is to create a dictionary that records the cosine similarities for every NP4 log likelihood collocation file for every word in the LXX and NT.
So each word will have its own file, e.g., CosSim_θεός.txt
Each individual file will be a dictionary made up of a single key (e.g., θεός), and the value for this key is a dictionary where the keys are the other words
and the values are the cosine similarities for that word and the target word.
So a small example would be {'θεός','Lemma'\n'κύριος',.568\nσωτήρ:.523\n...
'''
import re
import pickle
import math
import os.path
import decimal
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
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
    return dotprod / (magA * magB) 
CollDir = askdirectory(title = 'In which directory are your source files stored?')
FileList = os.listdir(CollDir) #extracts all the file names from the collocation list directory.  The program then goes through every file in this list to calculate significance of the co-occurrences.
DestDir = askdirectory(title = 'In which directory would you like to store the resulting similarity lists?', initialdir = CollDir)
#The following loop creates the LLDict that contains the collocates and LL values for every lemma.
#It has the form, e.g., {'θεός':{'κύριος':75.8554929234818, ἐγώ:20.2976784605015...
#Doing this here means I won't have to create the dictionaries for each word multiple times.
LLDict_Complete = {}
LemmaList = []
for file in FileList:
    Lemma = re.sub(r'Coll_([^_]+)_[^.]+.txt', r'\1', file)
    #print(file)
    LLFilename = CollDir + '/' + file #sets the absolute path for the source file
    if os.path.isfile(LLFilename) is True:
        LemmaList.append(Lemma)
        LLFile = open(LLFilename, mode = 'r', encoding = 'utf-8') #opens the source file
        LLDictLemm = {}
        for line in LLFile:
            if 'Lemma' in line:
                continue
            else:
                LLDictLemms = re.sub(r'([^ ]+) [^ ]+ ([^\n]+)\n', r'\1', line)
                #print(LLDictLemms)
                LLDictVals = float(re.sub(r'([^ ]+) [^ ]+ ([^\n]+)\n', r'\2', line))
                if LLDictVals >= 6.63 or LLDictVals <= -6.63: # this puts the cutoff probability according to chi-squared at 1%
                    LLDictLemm[LLDictLemms] = LLDictVals
        LLDict_Complete[Lemma] = LLDictLemm
        LLFile.close()
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