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
from decimal import *
def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames located?')
    dicts = askdirectory(title = 'Where are you lem dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    VSM_list = sorted([x for x in os.listdir(orig_dir) if x.endswith('pickle')])
    dicts_list = sorted([x for x in os.listdir(dicts) if x.endswith('pickle')])
    file_list = zip(VSM_list, dicts_list)
    df_dict_dict = {}
    for df, d in file_list:
        df_dict_dict[df] = d
    return df_dict_dict, dest_dir, dicts, orig_dir
def log_like(row):
    import numpy as np
    #values for c1
    C1 = lem_counts[row] #this value will be the same throughout a whole row
    #values for c2
    #here I need a Series that has all the values for all of the words
    C2 = lem_counts
    '''
    values for c12
    '''
    C12 = Coll_df.ix[row] #this is the row in the coll_df that I am looking at
    #values for p
    '''
    Just dividing C2 by N would gives the probability that any one word is word 2.
    Since we are working with an 8 word window, the probability that word 2 occurs in this window
    is actually 8 times the probability that any one word in that window is word 2.  Thus we
    multiply the probability by 8 in order to correct for this and set the maximum value for P
    at .99999 (it can't be more probable than 100%).
    '''
    P = np.fmin(1-((1-(C2/N))**8), .99) #N is the total number of words
    #values for p1
    P1 = C12/C1
    #values for p2
    P2 = (C2-C12)/(N-C1)
    '''
    In the calculations below, we replace -inf with zero.  This will only happen if we try to
    take the log of 0.  So if either of our np.power calculations is 0, this will occur.
    One of them could be 0 for the following reasons.
    1) if P == 0.  This would mean that the word does not occur in our corpus.  We won't
    be doing any calculations for words that don't occur in our corpus.
    2) if P == 1.  This will happen if the chance of word 2 occuring in the 8-word
    window is 100%.  This is only relevant for LL1 and LL2 (so measures of independence).
    Since the np.power calculations will always be below 1 (neither P nor 1-P can be more than 1),
    the np.log of a number between 0 and 1 will always be negative.  So the maximum value for
    independence is 0.  Therefore, if we expect a word to occur all of the time by chance in the
    8-word window, we must set the independence value to its maximum, i.e., 0).
    3) One of the P values (P, P1, P2) are so small and the value of the exponent is so high that
    the number goes under the minimum value that np.float128 can track (i.e., 10**-4551).  The only
    time this will occur is if the exponents are VERY large, which would only realistically happen when
    C1-C12 is very large, i.e., word 1 occurs extremely more often than it collocates with word 2, or
    vice versa, if C2-C12 is very large, meaning that word 2 occurs extremely more often outside of
    instead of inside of collocation with word 1.  Both of these would happen in such rare cases, I will
    ignore the possibility for now and leave -inf there now and recalculate them later using the
    Decimal package.
    '''
    LL1 = np.log(np.power(np.float128(P), C12)*np.power(np.float128(1-P), C1-C12))#.replace([-np.inf], [0])
    LL2 = np.log(np.power(np.float128(P), C2-C12)*np.power(np.float128(1-P), (N-C1)-(C2-C12)))# .replace([-np.inf], [0])
    LL3 = np.log(np.power(np.float128(P1), C12)*np.power(np.float128(1-P1), C1-C12))
    LL4 = np.log(np.power(np.float128(P2), C2-C12)*np.power(np.float128(1-P2), (N-C1)-(C2-C12)))
    LL = -2*(LL1+LL2-LL3-LL4)
    return LL

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

file_dict, dest_dir, dicts, orig_dir = file_dict_builder()
for df_file, lem_file in file_dict.items():
    print('Now analyzing %s'% df_file)
    LL_dest_file = '/'.join([dest_dir, ''.join([df_file.rstrip('_coll.pickle'), '_LL.pickle'])])
    #LL_p_dest_file = '/'.join([dest_dir, ''.join([df_file.rstrip('_coll.pickle'), '_LL_p.pickle'])])
    if os.path.isfile(LL_dest_file) and os.path.isfile(LL_p_dest_file):
        continue
    else:
        lem_counts, N = counter('/'.join([dicts, lem_file]))
        Coll_df = pd.read_pickle('/'.join([orig_dir, df_file]))
        LL_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
        #LL_p_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
        my_counter = 0
        for row in Coll_df.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'% (my_counter, len(Coll_df), datetime.datetime.now().time().isoformat()))
            LL_df.ix[row] = log_like(row)
            my_counter += 1
        LL_df.to_pickle(LL_dest_file)
        #LL_p_df.to_pickle(LL_p_dest_file)
