'''
To apply the log-likelihood function to every cell in a pandas DataFrame
use df.apply(function).  The function can then call the name and index of
the cell you are working on, and thus call values from other DataFrames
'''

import pandas as pd
import numpy as np
from math import log
from tkinter.filedialog import askdirectory
import os.path
import datetime

def file_dict_builder():
    '''
    This function returns the origin directory for the co-occurrence
    DataFrames that will be used by the calculations, the destination
    directory where the resulting log-likelihood DataFrames will be saved,
    and the list of file names of the DataFrames
    '''
    
    orig = askdirectory(title= 'Where are your collocate DataFrames \
                                    located?')
    dest = askdirectory(title = 'Where would you like to save the \
                                     resulting files?')
    pan_list = sorted([x for x in os.listdir(orig) if
                       x.endswith('pos.pickle')])
    dict_list = sorted([x for x in os.listdir(orig) if
                       x.endswith('pos_dict.pickle')])
    return zip(pan_list, dict_list), dest, orig

def log_L(k,n,x):
    '''
    This function applies the correct values from the DataFrame to the
    binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
    '''
    return np.log(np.power(np.float128(x),k)
                  * np.power(np.float128(1-x),(n-k)))

def log_space_L(k,n,x):
    '''
    This function finds all the inf and -inf values in the Series s and
    corrects the NaN and inf values by moving the whole equation to the log
    space, so that ln((x**k)*(1-x)**(n-k)) = (ln(x)*k) + (ln(1-x)*(n-k))
    I use math.log here instead of np.log because all the values are
    scalars instead of Series and math.log is 10x faster than np.log
    '''
    #I have not implemented this function because it is actually a little
    #slower than running the same loop within the parent function (log_like)
    
    return (np.log(np.float128(x)) * np.float128((k))
            + (np.log(np.float128((1-x)) * np.float128((n-k)))))

def p_calc(c_1, c_2, c_12, n_):
    '''
    This function calculates P1 and P2 for each DataFrame row.
    '''
    p1 = c_12/c_1
    p2 = (c_2-c_12)/(n_-c_1)
    return p1, p2

def log_like(row, C2, P, N, C12):
    '''
    values for c12
    this is the row in the coll_df that I am looking at
    '''
    #value for C1 will be a scalar value used for all calculations on
    #that row
    C1 = C2.ix[row]
    #The values for P1 and P2 will be the same for the whole row
    #P1, P2 = p_calc(C1, C2, C12, N)
    P1 = C12/C1
    #values for p2
    P2 = (C2-C12)/(N-C1)

    '''
    The following lines call alternately the log_L and the log_space_L
    function.  The first will calculate most values correctly except where
    they underrun the np.float128 object (10**-4950).  Those cases will be
    dealt with by moving the calculations to log space, thus calculating the
    natural log before the float128 can be underrun when taking a very small
    P number to even a moderately large exponent.
    '''
    
    LL1 = log_space_L(C12, C1, P)

    '''
    The following finds all inf and -inf values in LL1 by
    moving calculations into log space.
    '''
    '''
    LL1_inf = LL1[np.isinf(LL1)]
    for ind in LL1_inf.index:
        try:
            LL1.ix[ind] = (log(P[ind])*C12[ind])+(log(1-P[ind])*(C1-C12[ind]))
        except ValueError as E:
            LL1.ix[ind] = 0
    '''

    LL2 = log_space_L((C2-C12), N-C1, P)

    '''
    The following finds all inf and -inf values in LL2 by
    moving calculations into log space.
    '''
    '''
    LL2_inf = LL2[np.isinf(LL2)]
    for ind in LL2_inf.index:
        try:
            LL2.ix[ind] = (log(P[ind])*(C2[ind]-C12[ind]))+\
                          (log(1-P[ind])*((N-C1)-(C2[ind]-C12[ind])))
        except ValueError as E:
            LL2.ix[ind] = 0
    '''

    LL3 = log_space_L(C12, C1, P1)

    '''
    The following finds all inf and -inf values in LL3 by
    moving calculations into log space.
    '''
    '''
    LL3_inf = LL3[np.isinf(LL3)]
    for ind in LL3_inf.index:
        try:
            LL3.ix[ind] = (log(P1[ind])*C12[ind])+\
                          (log(1-P1[ind])*(C1-C12[ind]))
        except ValueError as E:
            LL3.ix[ind] = 0
    '''

    LL4 =log_space_L(C2-C12, N-C1, P2)

    '''
    The following finds all inf and -inf values in LL4 by
    moving calculations into log space.
    '''
    '''
    LL4_inf = LL4[np.isinf(LL4)]
    for ind in LL4_inf.index:
        try:
            LL4.ix[ind] = (log(P2[ind])*(C2[ind]-C12[ind]))+\
                          (log(1-P2[ind])*((N-C1)-(C2[ind]-C12[ind])))
        except ValueError as E:
            LL4.ix[ind] = 0
    '''
    return -2 * (LL1 + LL2 - LL3 - LL4)

pan_dict, dest_dir, orig_dir = file_dict_builder()

for pan_file, dict_file in pan_dict:
    print('Now analyzing %s'% pan_file)
    #If you want a different naming convention for your files,
    #simply change the line below
    LL_dest_file = os.path.join(dest_dir,''.join([pan_file.rstrip('.pickle'),
                                                  '_LL.pickle']))
    LL_txt_file = os.path.join(dest_dir,''.join([pan_file.rstrip('.pickle'),
                                                  '_LL.txt']))
    if os.path.isfile(LL_dest_file):
        continue
    else:
        coll_pan = pd.read_pickle(os.path.join(orig_dir, pan_file))
        n = np.sum(coll_pan.values)/40
        c2 = np.sum(np.sum(coll_pan))/40
        p = c2/n
        LL_pan = pd.Panel(items=coll_pan.items,
                          major_axis=coll_pan.major_axis,
                          minor_axis=coll_pan.minor_axis,
                          dtype=np.float128)
        for pos in coll_pan:
            my_counter = 0
            LL_pan.ix[pos] = log_like(pos, c2, p, n,
                                      coll_pan.ix[pos].T).T
        LL_pan = LL_pan.fillna(0)
        LL_pan.to_pickle(LL_dest_file)
        with open(LL_txt_file, mode='w') as f:
            for pos in LL_pan:
                s = ''.join([pos, '\n', LL_pan.ix[pos].to_string(), '\n\n'])
                f.write(s)