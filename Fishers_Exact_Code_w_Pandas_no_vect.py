'''
To apply the fisher_exact function to every cell in a pandas DataFrame
use df.apply(function).  The function can then call the name and index of
the cell you are working on, and thus call values from other DataFrames
'''
import pandas as pd
import numpy as np
from scipy.stats import fisher_exact
from tkinter.filedialog import askdirectory
import os.path
import datetime
from math import factorial # This is faster on normal integers than the scipy function

def m_f(x):
    # takes a Series as input, rounds the values, and then returns as Series of the factorials
    x = np.round_(x)
    return x.apply(factorial)

def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames located?')
    #dicts = askdirectory(title = 'Where are your lem_dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    file_list = sorted([x for x in os.listdir(orig_dir) if x.endswith('.pickle')])
    #dict_list = sorted([x for x in os.listdir(dicts) if x.endswith('.pickle')])
    #df_dict_list = zip(file_list, dict_list)
    #for file in file_list:
    #    if file.endswith('Coll.pickle'):
    #        df_dict_dict[file] = ''.join([file.split('.')[0], '_lem_dict.pickle'])
    return dest_dir, file_list, orig_dir

def fishers_calc(x):
    #For Fisher's exact test, we need first to construct a 2x2 contingency table like the one below
    #      |    w2    |    -w2    |
    #------------------------------
    #  w1  | c(w1,w2) | c(w1,-w2) |  c(w1)
    #--------------------------------------
    #  -w1 | c(-w1,w2)|c(-w1,-w2) |  c(-w1)
    #--------------------------------------
    #      |   c(w2)  | c(-w2)    |   N
    #
    #c(w1,w2) is the value in the cell in Series x that we are investigating
    #c(w1,-w2) is c(w1)-c(w1,w2).  c(w1) is extracted by looking up the word that is the 'name' of the Series x and finding its value in the lem_counts Series
    #c(-w1,w2) is c(w2)-c(w1,w2).  c(w2) is the cell in lem_counts that matches the cell we are dealing with now, i.e., has the same index.
    #Thus, c(w2) can be accessed simply by calling lem_counts since all calculations will be vectorized and thus matched.
    #c(-w1,-w2) is either c(-w2)-c(w1,-w2) or c(-w1)-c(-w1,w2).
    #And since c(-w2) (or -w1) is N-c(w2), we can rewrite this as N-c(w2)-c(w1,-w2).
    #And since c(w1,-w2) is c(w1)-c(w1,w2), then this can be rewritten as N-c(w2)-(c(w1)-c(w1,w2)) or N-c(w2)-c(w1)+c(w1,w2).
    #Adding c(w1,w2) back at the end corrects for the number of times that w1 appears with w2 that were already counted in c(w2)
    c1 = np.sum(Coll_df.ix[row])/8 #the count of the target word (names of the row in the df)
    c12 = Coll_df.ix[row]
    #c2 = lem_counts # This is calculated at the table level, not at the row level.
    a = c12
    b = np.fmax(c2 - c12, 0)
    c = np.fmax(c1 - c12, 0)
    d = N - c2 - c1 + c12
    data = {'a': a, 'b': b, 'c': c, 'd': d}
    fe_df = pd.DataFrame(data)
    new_row = pd.Series(index = Coll_df.index)
    for index, v in fe_df.iterrows():
        odds, p = fisher_exact([[v[0], v[1]],[v[2], v[3]]]) #I haven't been able to get this to work with vectorization.
        new_row.ix[index] = p
    '''
    The following is taken from Moore, "On Log-Likelihood and the Significance of Rare Events",
    http://research.microsoft.com/pubs/68957/rare-events-final-rev.pdf
    (c(w1)!c(-w1)!c(w2)!c(-w2)!) / N!c(w1,w2)!c(-w1,w2)!c(w1,-w2)!c(-w1,-w2)!
    c(-w1) = c+d
    c(w2) has already been converted to a factorial Series (fact_c2) at the table level
    c(-w2) has already been converted to a factorial Series (fact_-c2) at the table level
    c(w1,w2) = a
    c(-w1,w2) = b
    c(w1,-w2) = c
    c(-w1,-w2) = d
    '''
    #p = (factorial(round(c1))*m_f(c+d)*fact_c2*fact_nc2)/(fact_N*m_f(a)*m_f(b)*m_f(c)*m_f(d))
    return new_row

def counter(lem_dict_filename):
    #constructs a series of the total counts of all of the lemmata from the lem_dict
    #returns this series and N, the total number of words in the corpus
    lem_dict = pd.read_pickle(lem_dict_filename)
    #new_dict = {}
    #for key, value in lem_dict.values():
    #    new_dict[key] = value['count']
    lem_counts = pd.Series(lem_dict)
    N = lem_counts.sum()
    return lem_counts, N

dest_dir, file_list, orig_dir = file_dict_builder()

for file in file_list:
    print('Analyzing %s at %s' % (file, datetime.datetime.now().time().isoformat()))
    dest_file = ''.join([dest_dir, '/', file.rstrip('_coll.pickle')[0], '_FE.pickle'])
    #lem_counts, N = counter('/'.join([dicts, lem_file]))
    Coll_df = pd.read_pickle('/'.join([orig_dir, file]))
    N = np.sum(Coll_df.values)/8
    c2 = np.sum(Coll_df)/8
    FE_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
    my_counter = 0
    for row in Coll_df.index:
        if my_counter % 100 == 0:
            print('Row %s of %s at %s'% (my_counter, len(Coll_df), datetime.datetime.now().time().isoformat()))
        my_counter += 1
        FE_df.ix[row] = fishers_calc(row)
    FE_df.to_pickle(dest_file)
