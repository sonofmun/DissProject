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
    DF_list = sorted([x for x in os.listdir(orig) if
                       x.endswith('pickle')])
    return DF_list, dest, orig

def log_L(k,n,x):
    '''
    This function applies the correct values from the DataFrame to the
    binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
    '''
    return np.log((x**k)*((1-x)**(n-k)))

def log_space_L(s, k,n,x):
    '''
    This function finds all the inf and -inf values in the Series s and
    corrects the NaN and inf values by moving the whole equation to the log
    space, so that ln((x**k)*(1-x)**(n-k)) = (ln(x)*k) + (ln(1-x)*(n-k))
    I use math.log here instead of np.log because all the values are
    scalars instead of Series and math.log is 10x faster than np.log
    '''
    s_inf = s[np.isinf(s)]
    for ind in s_inf.index:
        s.ix[ind] = (log(x[ind])*k[ind]) + (log(1-x[ind])*(n-k[ind]))
    return s

def p_calc(c_1, c_2, c_12, n_):
    '''
    This function calculates P1 and P2 for each DataFrame row.
    '''
    p1 = c_12/c_1
    p2 = (c_2-c_12)/(n_-c_1)
    return p1, p2

def log_like(row, C2, P, N):
    '''
    values for c12
    this is the row in the coll_df that I am looking at
    '''
    C12 = Coll_df.ix[row]
    #value for C1 will be a scalar value used for all calculations on
    #that row
    C1 = np.sum(C12)/8
    #The values for P1 and P2 will be the same for the whole row
    P1, P2 = p_calc(C1, C2, C12, N)

    '''
    The following lines call alternately the log_L and the log_space_L
    function.  The first will calculate most values correctly except where
    they underrun the np.float128 object (10**-4950).  Those cases will be
    dealt with by moving the calculations to log space, thus calculating the
    natural log before the float128 can be underrun when taking a very small
    P number to even a moderately large exponent.
    '''
    
    LL1 = log_L(C12, C1, P)

    '''
    The following finds function corrects all inf and -inf values in LL1 by
    moving calculations into log space.
    '''

    LL1 = log_space_L(LL1, C12, C1, P)
    
    LL2 = log_L(C2-C12, N-C1, P)

    '''
    The following finds function corrects all inf and -inf values in LL2 by
    moving calculations into log space.
    '''

    LL2 = log_space_L(LL2, C2-C12, N-C1, P)

    LL3 = log_L(C12, C1, P1)
    
    '''
    The following finds function corrects all inf and -inf values in LL3 by
    moving calculations into log space.
    '''

    LL3 = log_space_L(LL3, C12, C1, P1)

    LL4 = log_L(C2-C12, N-C1, P2)

    '''
    The following finds function corrects all inf and -inf values in LL4 by
    moving calculations into log space.
    '''

    LL4 = log_space_L(LL4, C2-C12, N-C1, P2)
    
    return -2*(LL1+LL2-LL3-LL4)

DFs, dest_dir, orig_dir = file_dict_builder()

for df_file in DFs:
    print('Now analyzing %s'% df_file)
    #If you want a different naming convention for your files,
    #simply change the line below
    LL_dest_file = os.path.join(dest_dir,
                                 ''.join([df_file.rstrip('_coll.pickle'),
                                          '_LL.pickle']))
    if os.path.isfile(LL_dest_file):
        continue
    else:
        Coll_df = pd.read_pickle(os.path.join(orig_dir, df_file))
        n = np.sum(Coll_df.values)/8 
        #values for C2
        c2 = np.sum(Coll_df)/8
        #values for p
        p = c2/n 
        LL_df = pd.DataFrame(0., index = Coll_df.index,
                             columns = Coll_df.index, dtype = np.float128)
        my_counter = 0
        for row in Coll_df.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'%
                      (my_counter, len(Coll_df),
                       datetime.datetime.now().time().isoformat()))
            LL_df.ix[row] = log_like(row, c2, p, n)
            my_counter += 1
        LL_df.to_pickle(LL_dest_file)
