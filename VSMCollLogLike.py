'''
Created on 25.01.2014

@author: matthew.munson
'''
import re
import math
import os.path
import decimal
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import numpy as np
CollVSM = askopenfilename(title = 'Where is your collocate VSM located?')
with open(CollVSM, encoding = 'utf-8', newline = '\n') as CollFile:
    CollList = [x.rstrip('\n') for x in CollFile.readlines()]
headings = [x.strip(" '") for x in CollList.pop(0).split(',')]
formats = ['<U30'] #initiates the list that will become the list of the object types of the columns, setting the type of the first column (the target word)
[formats.append('int') for x in range(len(headings)-1)] #finishes creating the list of column object types, typing them all as floating point depending on the number of lexical types that exist in the original document.
mydescriptor = {}
CollList = [x.split(', ') for x in CollList] #this separates each element in CollList (each of which are str) into individual elements
#the following loop transforms each numerical element in CollList into an int type
for i, line in enumerate(CollList):
    for i2, element in enumerate(line):
        try:
            line[i2] = int(element)
        except ValueError as E:
            line[i2] = element.strip("'")
            continue
    testlist[i] = line
#The following will not work.  I cannot assign the dtypes to it.  I might need to create a zeroes array and then fill each value manually.
VSM = np.array(CollList)
decimal.getcontext().Emin = -425000000
for file in FileList:    #iterates through the collcation files in the source directory
    LLCollList = ''
    Lemma = re.sub(r'Coll_([^\']+)_[^_]+_NP4.txt', r'\1', file)
    LemCount = lemlist.count(Lemma)
    CollFilename = CollDir + '/' + file #sets the absolute path for the source file
    CollFile = open(CollFilename, mode = 'r', encoding = 'utf-8') #opens the source file
    LLfile = re.sub(r'.txt', r'_LL.txt', file) #sets the name of the destination file dependent on the name of the source file
    LLFileName = CollDir + "/LL/" + LLfile #sets the absolute path for the destination file
    if os.path.isfile(LLFileName) == True: #checks to see if a collocation file already exists for this lemma
        continue #if a collocation file for this lemma exists, it breaks out of the if loop and selects the next member of lemlist
    else: #this triggers if the significance file does not yet exist
        LLListFile = open(LLFileName, mode = 'w', encoding = 'utf-8') #opens the destination file for writing in utf-8
        for line in CollFile: # iterates through each line in the source file
            line = line.strip('\'\n') # = re.sub(r'\"', '', line, count = 1)
            if 'Lemma' in line:
                line = re.sub(r'\' ', r' ', line)
                LLLem = line + ' LL=NA\n'
                LLCollList = LLCollList + LLLem
                continue
            else:
                line = re.sub(r'\' ', r' ', line)
                CollCount = int(re.sub(r'[^\']+ ([0-9]+)', r'\1', line)) #extracts the number of co-occurrences
                CollLemCount = lemlist.count(re.sub(r'([^\']+) [0-9]+', r'\1', line)) #extracts the total number of occurrences of the lemma from the corpus.                Num = len(lemlist) #calculates the size of the corpus
                C1 = decimal.Decimal(LemCount) #this is the number of occurrences of the word under investigation
                C2 = decimal.Decimal(CollLemCount) #this is the number of times the co-occurrent occurs in the corpus
                C12 = decimal.Decimal(CollCount/8) #this is the number of times the original word and the co-occurrent occur together.  I divide by 8 because the number of occurrences is spread over a collocation window 8 words wide.
                P = decimal.Decimal(C2/Num) #the probability that a random word in the corpus will be the co-occurrent
                P1 = decimal.Decimal(C12/C1) #the probability that the co-occurrent will occur with the original lemma
                P2 = decimal.Decimal((C2 - C12)/(Num-C1)) #the probability that the co-occurrent occurs apart from the original lemma (I think)
                Test = C2-C12
                LL1 = decimal.log10(decimal.power(P, C12)*decimal.power(1-P, C1-C12))
                LL2 = decimal.log10(decimal.power(P, C2-C12)*decimal.power(1-P, Num-C1-C2-C12))
                if P1 == 1:
                    LL3 = 0 #I need to do this because otherwise decimal throws and error when it takes 0 to the 0 power
                else:
                    LL3 = decimal.log10(decimal.power(P1, C12)*decimal.power(1-P1, C1-C12))
                if P2 == 0:
                    LL4 = 0 #I need to do this because otherwise decimal throws and error when it takes 0 to the 0 power
                else:
                    LL4 = decimal.log10(decimal.power(P2, C2-C12)*decimal.power(1-P2, (Num-C1)-(C2-C12)))
                LL = -2*(LL1+LL2-LL3-LL4) #this is the calculation of the log likelihood adjusted to be referenced on a chi-squared table (i.e., *-2)
                LLColl = line + ' ' + str(LL) + '\n'
                LLCollList = LLCollList + LLColl
        LLCollStr = str(LLCollList)
        LLListFile.write(LLCollStr)
        LLListFile.close()
lemdoc.close()
