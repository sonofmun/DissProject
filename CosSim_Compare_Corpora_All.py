'''
This file will compare the same-indexed rows of two DataFrames to each
other using the cosine similarity metric.
'''

import pandas as pd
import numpy as np
from tkinter.filedialog import askdirectory, askopenfilename
from sklearn.metrics.pairwise import pairwise_distances as p_d
import datetime
import os.path

CCAT = askdirectory(title = 'Where are your original CCAT files located?')
GNT = askopenfilename(title = 'Where is your original GNT file located?')
dest = askdirectory(title = 'Where would you like to save your resulting comparison files?')
files1 = sorted([os.path.join(CCAT, x) for x in os.listdir(CCAT) if x.endswith('pickle')])
files1.append(GNT)


def fill_small(l, s):
    s_add = pd.DataFrame(index = l.index-s.index, columns = l.index-s.index)
    l_add = pd.DataFrame(index = s.index-l.index, columns = s.index-l.index)
    return l.append(l_add).fillna(0),s.append(s_add).fillna(0)    

for i in range(len(files1)):
    file1 = files1[i]
    df1 = pd.read_pickle(file1)
    df1[np.isinf(df1)] = 0
    for i2 in range(i+1, len(files1)):
        file2 = files1[i2]
        df2 = pd.read_pickle(file2)
        df2[np.isinf(df2)] = 0
        f1_name = os.path.split(file1)[1]
        f2_name = os.path.split(file2)[1]
        print('Filling the DFs at %s' % datetime.datetime.now().time().isoformat())
        df1_temp, df2 = fill_small(df1, df2)
        dest_file = ''.join([f1_name.split('_')[0], '_', f2_name.split('_')[0], '_', f2_name.split('_')[1], '.pickle'])
        match_file = ''.join([f1_name.split('_')[0], '_', f2_name.split('_')[0], '_', f2_name.split('_')[1], '_', 'matched.pickle'])
        print('Calculating the CS of %s and %s at %s' % (f1_name, f2_name, datetime.datetime.now().time().isoformat()))
        full_result = pd.DataFrame(p_d(df1_temp, df2, metric = 'cosine'), index = df1_temp.index, columns = df2.index)
        match_result = pd.Series(index = df1_temp.index)
        print('Filling matched results series at %s' % datetime.datetime.now().time().isoformat())
        for row in full_result:
            match_result.ix[row] = full_result.ix[row, row]
        del df1_temp
        del df2
        print('Writing %s at %s' % (dest_file, datetime.datetime.now().time().isoformat()))
        full_result.to_pickle(os.path.join(dest, dest_file))
        del full_result
        print('Writing %s at %s' % (match_file, datetime.datetime.now().time().isoformat()))
        match_result.to_pickle(os.path.join(dest, match_file))
        del match_result

        '''
        if len(df1)>len(df2):
            df1_temp, df2 = fill_small(df1, df2)
        else:
            df2, df1_temp = fill_small(df2, df1)
        counter = 0
        for row in df1_temp:
            if counter % 1000 == 0:
                print('Processing row %s of %s at %s' % (counter, len(df1_temp), datetime.datetime.now().time().isoformat()))
            s.ix[row] = p_d(df1_temp.ix[row], df2.ix[row], metric = 'cosine')
            counter += 1
        #Need to separate the actual filename frome the path below
        del df1_temp
        del df2
        f1_name = os.path.split(file1)
        f2_name = os.path.split(file2)
        dest_file = ''.join([f1_name.split('_')[0], '_', f2_name.split('_')[0], '_', f2_name.split('_')[1], '.pickle'])
        s.to_pickle(os.path.join(dest, dest_file))
        '''
