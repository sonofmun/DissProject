'''
This file will compare the same-indexed rows of two DataFrames to each
other using the cosine similarity metric.
'''

import pandas as pd
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
    l_add = pd.DataFrame(index = s.index-l.index, dolumns = s.index-l.index)
    return l.append(l_add).fillna(0),s.append(s_add).fillna(0)    

for i in range(len(files1)):
    file1 = files1[i]
    df1 = pd.read_pickle(file1)
    s = pd.Series(index = df1.index)
    for i2 in range(i+1, len(files1)):
        file2 = files1[i2]
        print('Calculating the CS of %s and %s at %s' % (file1, file2, datetime.datetime.now().time().isoformat()))
        df2 = pd.read_pickle(file2)
        if len(df1)>len(df2):
            df1_temp, df2 = fill_small(df1, df2)
        else:
            df2, df1_temp = fill_small(df2, df1)
        for row in df1_temp:
            s.ix[row] = p_d(df1.ix[row], df2.ix[row])
        #Need to separate the actual filename frome the path below
        del df1_temp
        dest_file = ''.join([file1.split('_')[0], '_', file2.split('_')[0], '_', file2.split('_')[1], '.pickle'])
        s.to_pickle(os.path.join(dest, dest_file))
