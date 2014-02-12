'''
Created on 30.04.2013
by Matthew Munson
The purpose of this file is to run a cosine similarity comparison between every word in the collocation array.
The resulting file will be a csv file with 1 line for headings, then one line for each lemma, with the CS scores for each
word in the heading arranged under it.
'''
import decimal as deci
from numpy import *
from tkinter.filedialog import asksaveasfilename, askopenfilename
LLVSMFile = askopenfilename(title = 'Where is your log likelihood VSM located?')
CSVSMFile = asksaveasfilename(title = 'Where would you like to save your cosine similarity VSM file?')
deci.getcontext().prec = 999999999999999999
def NP4LL_cosine_similarity(c1, c2):
    dotprod = deci.Decimal('0')
    magA = deci.Decimal('0')
    magB = deci.Decimal('0')
    for i in range(2, len(LLVSM.dtype.names)-1):
        dotprod = deci.Context().add(dotprod, deci.Context().multiply(deci.Decimal(str(LLVSM[c1][i])), deci.Decimal(str(LLVSM[c2][i]))))
        magA = deci.Context().add(magA, deci.Context().power(deci.Decimal(str(LLVSM[c1][i])), 2))
        magB = deci.Context().add(magB, deci.Context().power(deci.Decimal(str(LLVSM[c2][i])), 2))
    magA = deci.Context().sqrt(magA)
    magB = deci.Context().sqrt(magB)
    #returns the cosine similarity of the two dictionaries
    try:
        return deci.Context().divide(dotprod, deci.Context().multiply(magA, magB)) 
    except ZeroDivisionError as E:
        return 0
'''
The following loop constructs a numpy array from the LL VSM file
'''
with open(r'C:\Users\mam3tc\Documents\GitHub\DissProject\CCAT\CCATCollCount\test_LL.txt', encoding = 'utf-8') as LLfile:
    headstr = LLfile.readline()
    headings = headstr.replace("'", '').rstrip('\n').split(',')
    formats = ['<U30', 'int']
    [formats.append('float') for x in range(len(headings)-1)]
    mydescriptor = {'names': headings, 'formats': formats}
    LLVSM = loadtxt(LLfile, delimiter = ',', dtype = mydescriptor)
LLRange = range(len(LLVSM)) #this range object will be used in the loops below
CSVSM = zeros(len(LLVSM), dtype = mydescriptor) #empty array to be filled with Cosine Similarity scores
'''
the following loop goes through the whole LLVSM array, calculates to the Cosine Similarity score
for every word in the array, and then writes it to the CSVSM array.
'''
for i1 in LLRange:
    c1List = [LLVSM[i1][0], LLVSM[i1][1]]
    for i2 in LLRange:
        CSScore = NP4LL_cosine_similarity(i1, i2)
        c1List.append(CSScore)
    CSVSM[i1] = tuple(c1List)
with open(CSVSMFile, mode = 'w', encoding = 'utf-8') as CSFile:
    CSFile.write(''.join([str(CSVSM.dtype.names).strip('()').replace(' ', ''), '\n']))
    savetxt(CSFile, CSVSM, delimiter = ',', fmt = '%s')

