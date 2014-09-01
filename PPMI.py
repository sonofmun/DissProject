__author__ = 'matt'

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

def PMI_calc(row, P2, N, colls):
    '''
    values for c12
    this is the row in the coll_df that I am looking at
    '''
    C12 = colls.ix[row]
    #value for C1 will be a scalar value used for all calculations on
    #that row
    C1 = np.sum(C12)
    P1 = C1/N
    P12 = C12/N

    return np.log2(np.divide(P12,P1*P2))


def PMI():
    """Runs a log-likelihood computation on a series of collocation
DataFrames in a specific directory, saving them to a new directory.
    """
    DFs, dest_dir, orig_dir = file_dict_builder()

    for df_file in DFs:
        print('Now analyzing %s'% df_file)
        #If you want a different naming convention for your files,
        #simply change the line below
        PMI_dest_file = os.path.join(dest_dir,
                                     ''.join([df_file.rstrip('_coll.pickle'),
                                              '_PMI.pickle']))
        if os.path.isfile(PMI_dest_file):
            continue
        else:
            Coll_df = pd.read_pickle(os.path.join(orig_dir, df_file))
            n = np.sum(Coll_df.values)
            p2 = np.sum(Coll_df)/n
            PMI_df = pd.DataFrame(0., index=Coll_df.index,
                                 columns=Coll_df.index, dtype=np.float128)
            my_counter = 0
            for row in Coll_df.index:
                if my_counter % 100 == 0:
                    print('Row %s of %s at %s'%
                          (my_counter, len(Coll_df),
                           datetime.datetime.now().time().isoformat()))
                PMI_df.ix[row] = PMI_calc(row, p2, n, Coll_df)
                my_counter += 1
            PMI_df[PMI_df<0] = 0
            PMI_df.to_pickle(PMI_dest_file)

def pmi_unit_test(c1, c2, c12, n):
    p1 = c1/n
    p2 = c2/n
    p12 = c12/n
    return np.log2(p12)-(np.log2(p1*p2))

