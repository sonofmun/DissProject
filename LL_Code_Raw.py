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
from decimal import Decimal as deci, InvalidOperation
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
    c1 = np.sum(Coll_df.ix[row])
    C1 = c1/8 #this value will be the same throughout a whole row
    #values for c2
    #here I need a Series that has all the values for all of the words
    #C2 = np.sum(Coll_df.values)
    '''
    values for c12
    '''
    C12 = Coll_df.ix[row] #this is the row in the coll_df that I am looking at
    #values for p
    #P = C2/N #N is the total number of words. This is being calculated at the table level instead of the row level since at that point we know C2 and we know N.
    #values for p1
    #P1 = C12/c1 #this is wrong!  Corrected below.
    P1 = C12/C1
    #values for p2
    P2 = (C2-C12)/(N-C1)
    LL1 = np.log(np.power(np.float128(P), C12)*np.power(np.float128(1-P), C1-C12))
    LL1_inf = LL1[np.isinf(LL1)]
    for ind in LL1_inf.index:
        try:
            LL1.ix[ind] = np.float128((np.power(deci(P.ix[ind]), deci(int(C12.ix[ind])))*np.power(deci(1-P.ix[ind]), deci(int(C1-C12.ix[ind])))).ln())
        except InvalidOperation as E:
            LL1.ix[ind] = 0
    LL2 = np.log(np.power(np.float128(P), C2-C12)*np.power(np.float128(1-P), (N-C1)-(C2-C12)))
    LL2_inf = LL2[np.isinf(LL2)]
    for ind in LL2_inf.index:
        try:
            LL2.ix[ind] = np.float128((np.power(deci(P.ix[ind]), deci(int(C2.ix[ind]-C12.ix[ind])))*np.power(deci(1-P.ix[ind]), deci(int((N-C1)-(C2.ix[ind]-C12.ix[ind]))))).ln())
        except InvalidOperation as E:
            LL2.ix[ind] = 0
    LL3 = np.log(np.power(np.float128(P1), C12)*np.power(np.float128(1-P1), C1-C12))
    LL3_inf = LL3[np.isinf(LL3)]
    for ind in LL3_inf.index:
        try:
            LL3.ix[ind] = np.float128((np.power(deci(P1.ix[ind]), deci(int(C12.ix[ind])))*np.power(deci(1-P1.ix[ind]), deci(int(C1-C12.ix[ind])))).ln())
        except InvalidOperation as E:
            LL3.ix[ind] = 0
    LL4 = np.log(np.power(np.float128(P2), C2-C12)*np.power(np.float128(1-P2), (N-C1)-(C2-C12)))
    LL4_inf = LL4[np.isinf(LL4)]
    for ind in LL2_inf.index:
        try:
            LL4.ix[ind] = np.float128((np.power(deci(P2.ix[ind]), deci(int(C2.ix[ind]-C12.ix[ind])))*np.power(deci(1-P2.ix[ind]), deci(int((N-C1)-(C2.ix[ind]-C12.ix[ind]))))).ln())
        except InvalidOperation as E:
            LL4.ix[ind] = 0
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
    #N = lem_counts.sum()
    return lem_counts#, N

file_dict, dest_dir, dicts, orig_dir = file_dict_builder()
for df_file, lem_file in file_dict.items():
    print('Now analyzing %s'% df_file)
    LL_dest_file = '/'.join([dest_dir, ''.join([df_file.rstrip('_coll.pickle'), '_LL.pickle'])])
    #LL_p_dest_file = '/'.join([dest_dir, ''.join([df_file.rstrip('_coll.pickle'), '_LL_p.pickle'])])
    if os.path.isfile(LL_dest_file) and os.path.isfile(LL_p_dest_file):
        continue
    else:
        #lem_counts, N = counter('/'.join([dicts, lem_file]))
        #lem_counts = counter('/'.join([dicts, lem_file])) # This is only needed for the raw counts code
        #N = sum(lem_counts.values) # This is only needed for the raw counts code
        Coll_df = pd.read_pickle('/'.join([orig_dir, df_file]))
        N = np.sum(Coll_df.values)/8 # This is for the binary counts code
        #values for C2
        C2 = np.sum(Coll_df)/8
        #values for p
        P = C2/N #N is the total number of words
        LL_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index, dtype = np.float128)
        #LL_p_df = pd.DataFrame(0., index = Coll_df.index, columns = Coll_df.index)
        my_counter = 0
        for row in Coll_df.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'% (my_counter, len(Coll_df), datetime.datetime.now().time().isoformat()))
            LL_df.ix[row] = log_like(row)
            my_counter += 1
        LL_df.fillna(value = 0, inplace = True)
        LL_df.to_pickle(LL_dest_file)
        #LL_p_df.to_pickle(LL_p_dest_file)
