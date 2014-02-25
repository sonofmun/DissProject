'''
Created on 25.01.2014

@author: matthew.munson
'''
import re
import math
import os.path
import decimal as deci
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import numpy as np
CollVSMFile = askopenfilename(title = 'Where is your collocate VSM located?')
LLVSMFile = asksaveasfilename(title = 'Where would you like to save your log likelihood VSM file?')
with open(CollVSMFile, encoding = 'utf-8', newline = '\n') as CollFile:
    CollList = [x.rstrip('\n') for x in CollFile.readlines()]
headings = [x.strip(" '\r") for x in CollList.pop(0).split(',')]
formats = ['<U30'] #initiates the list that will become the list of the object types of the columns, setting the type of the first column (the target word)
[formats.append('int') for x in range(len(headings)-1)] #finishes creating the list of column object types, typing them all as floating point depending on the number of lexical types that exist in the original document.
mydescriptor = {'names': headings, 'formats': formats}
LLformats = ['<U30', 'int']
[LLformats.append('float') for x in range(len(headings)-1)]
LLdescriptor = {'names': headings, 'formats': LLformats}
CollList = [x.split(', ') for x in CollList] #this separates each element in CollList (each of which are str) into individual elements
CountDict = {}
#the following loop transforms each numerical element in CollList into an int type
for i, line in enumerate(CollList):
    for i2, element in enumerate(line):
        try:
            line[i2] = int(element)
        except ValueError as E:
            line[i2] = element.strip("'")
            continue
    CollList[i] = tuple(line)
    CountDict[CollList[i][0]] = CollList[i][1]
CollVSM = np.array(CollList, dtype = mydescriptor)
LLVSM = np.zeros(len(CollList), dtype = LLdescriptor)
deci.getcontext().Emin = -425000000
for i2, element in enumerate(CollVSM):
    element = tuple(element)
    Lemma = element[0]
    LemCount = element[1].astype(deci.Decimal)
    LLVSM[i2][0] = Lemma
    LLVSM[i2][1] = LemCount
    for i, CollCount in enumerate(element[2:]): # iterates through each line in the source file
        Collocate = headings[i+2]
        CollLemCount = CountDict[Collocate]
        Num = sum(CountDict.values())
        C1 = deci.Decimal(LemCount) #this is the number of occurrences of the word under investigation
        C2 = deci.Decimal(CollLemCount) #this is the number of times the co-occurrent occurs in the corpus
        C12 = deci.Decimal(CollCount.astype(deci.Decimal)/8) #this is the number of times the original word and the co-occurrent occur together.  I divide by 8 because the number of occurrences is spread over a collocation window 8 words wide.
        P = deci.Decimal(C2/Num) #the probability that a random word in the corpus will be the co-occurrent
        P1 = deci.Decimal(C12/C1) #the probability that the co-occurrent will occur with the original lemma
        P2 = deci.Decimal((C2 - C12)/(Num-C1)) #the probability that the co-occurrent occurs apart from the original lemma (I think)
        Test = C2-C12
        LL1 = deci.Decimal.log10(deci.Context().power(P, C12)*deci.Context().power(1-P, C1-C12))
        LL2 = deci.Decimal.log10(deci.Context().power(P, C2-C12)*deci.Context().power(1-P, Num-C1-C2-C12))#
        #if P1 == 1:
            #LL3 = 0 #I need to do this because otherwise decimal throws and error when it takes 0 to the 0 deci.power
        #elif P1 == 0:
        #    LL3 = 0
        #else:
        try:
            LL3 = deci.Decimal.log10(deci.Context().power(P1, C12)*deci.Context().power(1-P1, C1-C12))
        except deci.InvalidOperation as E:
            LL3 = 0
            continue
        #if P2 == 0:
        #    LL4 = 0 #I need to do this because otherwise decimal throws and error when it takes 0 to the 0 deci.power
        try:
            LL4 = deci.Decimal.log10(deci.Context().power(P2, C2-C12)*deci.Context().power(1-P2, (Num-C1)-(C2-C12)))
        except deci.InvalidOperation as E:
            LL4 = 0
            continue
        LL = -2*(LL1+LL2-LL3-LL4) #this is the calculation of the log likelihood adjusted to be referenced on a chi-squared table (i.e., *-2)
        LLVSM[i2][i+2] = LL
with open(LLVSMFile, mode = 'w', encoding = 'utf-8') as LLFile:
    LLFile.write(''.join([str(LLVSM.dtype.names).strip('()').replace(' ', ''), '\n']))
    np.savetxt(LLFile, LLVSM, delimiter = ',', fmt = '%s')
