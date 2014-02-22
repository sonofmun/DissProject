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
from sklearn.metrics.pairwise import pairwise_distances
#from scipy.spatial.distance import cosine
LLVSMFile = askopenfilename(title = 'Where is your log likelihood VSM located?')
CSVSMFile = asksaveasfilename(title = 'Where would you like to save your cosine similarity VSM file?')
deci.getcontext().prec = 425000000
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
def Txt_to_nparray():
    with open(LLVSMFile, encoding = 'utf-8') as LLfile:
        headstr = LLfile.readline()
        headings = headstr.replace("'", '').rstrip('\n').split(',')
        formats = ['<U30', 'int']
        [formats.append('float') for x in range(len(headings)-1)]
        mydescriptor = {'names': headings, 'formats': formats}
        cols_2_use = range(2, len(headings)-3)
        LLVSM = loadtxt(LLfile, delimiter = ',', dtype = mydescriptor)
    with open(LLVSMFile, encoding = 'utf-8') as LLfile:
        Short_LLVSM = loadtxt(LLfile, delimiter = ',', usecols = cols_2_use, skiprows = 1)
        return LLVSM, Short_LLVSM, mydescriptor
LLVSM, Short_LLVSM, mydescriptor = Txt_to_nparray()
LLRange = range(len(LLVSM)) #this range object will be used in the loops below
CSVSM = zeros(len(LLVSM), dtype = mydescriptor) #empty array to be filled with Cosine Similarity scores
CS_Dists = pairwise_distances(Short_LLVSM, metric = 'cosine', n_jobs = -1)
for i in range(len(CSVSM)-1):
    for i2 in range(len(CSVSM[i])-3):
        CSVSM[i][0] = LLVSM[i][0]
        CSVSM[i][1] = LLVSM[i][1]
        CSVSM[i][i2+2] = CS_Dists[i][i2]
'''
the following loop goes through the whole LLVSM array, calculates to the Cosine Similarity score
for every word in the array, and then writes it to the CSVSM array.
'''
with open(CSVSMFile, mode = 'w', encoding = 'utf-8') as CSFile:
    CSFile.write(''.join([str(CSVSM.dtype.names).strip('()').replace(' ', ''), '\n']))
    savetxt(CSFile, CSVSM, delimiter = ',', fmt = '%s')
