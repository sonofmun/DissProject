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

def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames located?')
    dicts = askdirectory(title = 'Where are your lem_dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    file_list = sorted([x for x in os.listdir(orig_dir) if x.endswith('.pickle')])
    dict_list = sorted([x for x in os.listdir(dicts) if x.endswith('.pickle')])
    df_dict_list = zip(file_list, dict_list)
    #for file in file_list:
    #    if file.endswith('Coll.pickle'):
    #        df_dict_dict[file] = ''.join([file.split('.')[0], '_lem_dict.pickle'])
    return df_dict_list, dest_dir, dicts, orig_dir

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
    c1 = lem_counts[x] #the count of the target word (names of the row in the df)
    c12 = Coll_df.ix[row]
    c2 = lem_counts
    a = c12
    b = c1-c12
    c = c2- 12
    d = N-c2-c1+c12
    odds, p = fisher_exact([[a, b],[c, d]])
    return p

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

file_list, dest_dir, dicts, orig_dir = file_dict_builder()

for df_file, lem_file in file_list:
    print('Analyzing %s at %s' % (df_file, datetime.datetime.now().time().isoformat()))
    dest_file = ''.join([dest_dir, df_file.rstrip('_coll.pickle')[0], '_FE.pickle'])
    lem_counts, N = counter('/'.join([dicts, lem_file]))
    Coll_df = pd.read_pickle('/'.join([orig_dir, df_file]))
    FE_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
    my_counter = 0
    for row in Coll_df.index:
        if my_counter % 100 == 0:
            print('Row %s of %s at %s'% (my_counter, len(Coll_df), datetime.datetime.now().time().isoformat()))
        FE_df.ix[row] = fishers_calc(row)
    FE_df.to_pickle(dest_file)
