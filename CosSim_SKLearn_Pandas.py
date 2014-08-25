'''
Created on 30.04.2013
by Matthew Munson
The purpose of this file is to run a cosine similarity comparison between
every word in the collocation array. The resulting file will be a csv file
with 1 line for headings, then one line for each lemma, with the CS scores
for each word in the heading arranged under it.
'''

import pandas as pd
import numpy as np
from tkinter.filedialog import askdirectory
from sklearn.metrics.pairwise import pairwise_distances
import datetime
import os.path


def CS():
    """This function calls the pairwise distance function from sklearn
    on every log-likelihood DataFrame in a certain directory and returns
    the similarity score (i.e., 1-cosine distance) for every word, saving
    the results then to a different directory.


    """
    LLs = askdirectory(title='Where are your log likelihood pickles located?')
    CSs = askdirectory(title='Where would you like to save your cosine '
                               'similarity pickles?')
    LLlist = sorted([x for x in os.listdir(LLs) if x.endswith('pickle')])

    for LLfile in LLlist:
        print('Now analyzing %s at %s' %
              (LLfile, datetime.datetime.now().time().isoformat()))
        LL = pd.read_pickle('/'.join([LLs, LLfile]))
        LL = LL.fillna(value=0)
        LL = LL.replace(to_replace=np.inf, value=0)
        CSfile = '_'.join([LLfile.rstrip('_LL.pickle'), 'CS.pickle'])
        #print('test')
        CS_Dists = 1-pairwise_distances(LL, metric='cosine', n_jobs = 1)
        CS = pd.DataFrame(CS_Dists, index=LL.index, columns=LL.index)
        CS.to_pickle('/'.join([CSs, CSfile]))
