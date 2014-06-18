'''
The purpose of this file is to recalculate nan values in every
LL DataFrame using Decimal objects instead of np.int128.
'''
import pandas as pd
import numpy as np
from decimal import Decimal as deci
from decimal import InvalidOperation
from tkinter.filedialog import askdirectory
import os
import datetime

coll_dir = askdirectory(title = 'Where are your collocation DataFrames?')
LL_dir = askdirectory(title = 'Where are your log-likelihood DataFrames?')
dest_dir = askdirectory(title = 'Where would you like to save the corrected files?')

coll_list = sorted([f for f in os.listdir(coll_dir) if f.endswith('.pickle')])
LL_list = sorted([f for f in os.listdir(LL_dir) if f.endswith('.pickle')])
files = zip(coll_list, LL_list)

'''
def load_counts():
    #calculates the c1, c2, and N counts from the collocation files for each corpus
    wc = np.sum(coll_df, axis = 1)
    num = np.sum(coll_df.values)
    return wc, num
'''
def find_nan():
    #returns the indices of every value in the df where np.isnan or np.isinf
    nans = {}
    for i in range(len(LL_df)):
        s = LL_df.ix[i]
        nan_list = list(s[np.isnan(s)].index)
        for ind in list(s[np.isinf(s)].index):
            nan_list.append(ind)
        nans[s.name] = nan_list
    return nans

def LL_calc(k, s):
    #recalculates LL using Decimal objects
    C1 = deci(np.sum(coll_df.ix[k])/8)
    C2 = deci(np.sum(coll_df.ix[:, s])/8)
    C12 = deci(int(coll_df.ix[k, s]))
    P = deci(C2/N)
    P1 = deci(C12/C1)
    P2 = deci((C2-C12)/(N-C1))
    LL1 = (np.power(P, C12)*np.power(1-P, C1-C12)).ln()
    LL2 = (np.power(P, C2-C12)*np.power(1-P, (N-C1)-(C2-C12))).ln()
    try:
        LL3 = (np.power(P1, C12)*np.power(1-P1, C1-C12)).ln()
    except InvalidOperation as E:
        LL3 = 0
    try:
        LL4 = (np.power(P2, C2-C12)*np.power(1-P2, (N-C1)-(C2-C12))).ln()
    except InvalidOperation as E:
        LL4 = 0
    LL = -2*(LL1+LL2-LL3-LL4)
    return np.float128(LL)

for colls, LLs in files:
    print('Analyzing %s at %s' % (LLs, datetime.datetime.now().time().isoformat()))
    coll_df = pd.read_pickle(os.path.join(coll_dir, colls))
    N = deci(np.sum(coll_df.values)/8)
    #word_counts, N = load_counts()
    LL_df = pd.read_pickle(os.path.join(LL_dir, LLs))
    nan_dict = find_nan()
    rows = len(nan_dict)
    counter = 0
    for key in nan_dict.keys():
        if counter % 1000 == 0:
            print('Now evaluating row %s of %s at %s' % (counter, rows, datetime.datetime.now().time().isoformat()))
        for sub_key in nan_dict[key]:
            LL_df.ix[key, sub_key] = LL_calc(key, sub_key)
        counter += 1
    nan_dict = None
    coll_df = None
    dest_file = os.path.join(dest_dir, ''.join([LLs.split('.')[0], '_corr_nans.pickle']))
    LL_df.to_pickle(dest_file)
    LL_df = None
    
