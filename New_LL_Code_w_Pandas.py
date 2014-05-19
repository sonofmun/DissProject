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
import datetime
def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames and lem_dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    file_list = os.listdir(orig_dir)
    df_dict_dict = {}
    for file in file_list:
        if file.endswith('coll.pickle'):
            df_dict_dict[file] = ''.join([file.split('.')[0], '_dict.pickle'])
    return df_dict_dict, dest_dir, orig_dir
def log_like(column, row):
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
    c1 = lem_counts[row] #the count of the target word (names of the row in the df)
    LL, p, dof, expected = chi2_contingency([[Coll_df.ix[column, row], max(c1-Coll_df.ix[column, row], 0)],[max(lem_counts[column]-Coll_df.ix[column, row],0), max(N-lem_counts[column]-c1+Coll_df.ix[column, row],0)]], lambda_ = 0)
    return LL, p
#The above returns one value for the whole row.  I need to figure out how to get it to return a value for each element.
#I have 2 Series (x, lem_counts) and one constant.  Can I somehow map the once series onto the other with the formulae above?  I will try tomorrow.
#something like: x.map(cont_funct(lem_counts))?  With cont_funct accepting the values and spitting out the elementwise answers?
#ref cont_func(x, y): chi2_contingency([[x, np.fmax(c1-x, 0)],[np.fmax(y-x, 0), np.fmax(N-y-c1+x)]], lambda_ = 0).  I might even be able to use max instead of fp.max.  I will test tomorrow.

def counter(lem_dict_filename):
    #constructs a series of the total counts of all of the lemmata from the lem_dict
    #returns this series and N, the total number of words in the corpus
    lem_dict = pd.read_pickle(lem_dict_filename)
    new_dict = {}
    for key, value in lem_dict.items():
        new_dict[key] = value
    lem_counts = pd.Series(new_dict)
    N = lem_counts.sum()
    return lem_counts, N

file_dict, dest_dir, orig_dir = file_dict_builder()
for df_file, lem_file in file_dict.items():
    print('Now analyzing %s'% df_file)
    LL_dest_file = '/'.join([dest_dir, ''.join([df_file.split('_')[0], '_LL.pickle'])])
    LL_p_dest_file = '/'.join([dest_dir, ''.join([df_file.split('_')[0], '_LL_p.pickle'])])
    if os.path.isfile(LL_dest_file) and os.path.isfile(LL_p_dest_file):
        continue
    else:
        lem_counts, N = counter('/'.join([orig_dir, lem_file]))
        Coll_df = pd.read_pickle('/'.join([orig_dir, df_file]))
        LL_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
        LL_p_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
        my_counter = 0
        for row in Coll_df.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'% (my_counter, len(Coll_df), datetime.datetime.now().time().isoformat()))
            for column in Coll_df.index:
                LL_df.ix[column, row], LL_p_df.ix[column, row] = log_like(column, row)
            my_counter += 1
        LL_df.to_pickle(LL_dest_file)
        LL_p_df.to_pickle(LL_p_dest_file)
