'''
Created on 30.04.2013
by Matthew Munson
The purpose of this file is to run a cosine similarity comparison between every word in the collocation array.
The resulting file will be a csv file with 1 line for headings, then one line for each lemma, with the CS scores for each
word in the heading arranged under it.
'''

import pandas as pd
import numpy as np
from tkinter.filedialog import askdirectory
from sklearn.metrics.pairwise import pairwise_distances
import datetime
import os.path

LLs = askdirectory(title = 'Where are your log likelihood pickles located?')
#dicts = askdirectory(title = 'Where are your coll_dict pickles located?')
CSs = askdirectory(title = 'Where would you like to save your cosine similarity pickles?')
LLlist = sorted([x for x in os.listdir(LLs) if x.endswith('pickle')])
#dictlist = sorted([x for x in os.listdir(dicts) if x.endswith('pickle')])
#file_list = zip(LLlist, dictlist)

'''
LLVSM, Short_LLVSM, mydescriptor = Txt_to_nparray()
LLRange = range(len(LLVSM)) #this range object will be used in the loops below
CSVSM = zeros(len(LLVSM), dtype = mydescriptor) #empty array to be filled with Cosine Similarity scores
LLVSM[:]['Lemma'] = CSVSM.dtype.names[2:]
'''
for LLfile in LLlist:
    print('Now analyzing %s at %s' % (LLfile, datetime.datetime.now().time().isoformat()))
    LL = pd.read_pickle('/'.join([LLs, LLfile]))
    LL = LL.fillna(value = 0)
    LL = LL.replace(to_replace = np.inf, value = 0)
    CSfile = '_'.join([LLfile.rstrip('_LL.pickle'), 'CS.pickle'])
    #print('test')
    CS_Dists = pairwise_distances(LL, metric = 'cosine', n_jobs = 1)
    CS = pd.DataFrame(CS_Dists, index = LL.index, columns = LL.index)
    CS.to_pickle('/'.join([CSs, CSfile]))

'''
the following loop goes through the whole LLVSM array, calculates to the Cosine Similarity score
for every word in the array, and then writes it to the CSVSM array.
'''