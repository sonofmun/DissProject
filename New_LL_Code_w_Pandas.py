'''
To apply the log-likelihood function to every cell in a pandas DataFrame
use df.apply(function).  The function can then call the name and index of
the cell you are working on, and thus call values from other DataFrames
'''
import pandas as pd
import numpy as np
from tkinter.filedialog import askdirectory
import os.path
from scipy.stats import chi2_contingency
def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames and lem_dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    file_list = os.listdir(orig_dir)
    df_dict_dict = {}
    for file in file_list:
        if file.endswith('Coll.pickle'):
            df_dict_dict[file] = ''.join([file.split('.')[0], '_lem_dict.pickle'])
    return df_dict_dict, dest_dir
def log_like(x):
    #For chi2 contingency test, we need first to construct a 2x2 contingency table like the one below
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
    c1 = lem_counts[x.name] #the count of the target word (names of the row in the df)
    LL, p, dof, expected = chi2_contingency([[x, max(c1-x, 0)],[max(lem_counts-x,0), max(N-lem_counts-c1+x,0)]], lambda_ = 0)
    return LL, p
#The above returns one value for the whole row.  I need to figure out how to get it to return a value for each element.

def counter(lem_dict_filename):
    #constructs a series of the total counts of all of the lemmata from the lem_dict
    #returns this series and N, the total number of words in the corpus
    lem_dict = pd.read_pickle(lem_dict_filename)
    new_dict = {}
    for key, value in lem_dict.values():
        new_dict[key] = value['count']
    lem_counts = pd.Series(new_dict)
    N = lem_counts.sum()
    return lem_counts, N

file_dict, dest_dir = file_dict_builder()
for df_file, lem_file in file_dict.items():
    LL_dest_file = ''.join([dest_dir, df_file.split('_')[0], '_LL.pickle'])
    LL_p_dest_file = ''.join([dest_dir, df_file.split('_')[0], '_LL_p.pickle'])
    lem_counts, N = lem_counter(lem_file)
    Coll_df = pd.read_pickle(df_file)
    LL_df, LL_p_df = Coll_df.apply(lambda x: log_like(x), axis = 1)
    LL_df.to_pickle(LL_dest_file)
    LL_p_df.to_pickle(LL_p_dest_file)
