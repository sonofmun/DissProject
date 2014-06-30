'''
The purpose of this script is to produce the data and the graphs for
a comparison of the word θεός in the different corpora as compared by
LL, CS, or whatever other data we load in.
'''

import pandas as pd #necessary for the DataFrames and Series
from tkinter.filedialog import askdirectory, askopenfilename
import matplotlib.pyplot as plt
import os

LN_file = askopenfilename(title = 'Where is your Louw-Nida dictionary?')
CCAT = askdirectory(title = 'Where are your CCAT data frames located?')
NT = askopenfilename(title = 'Where is the appropriate NT data frame?')
dest = askdirectory(title = 'Where would you like to save your results?')

files = [os.path.join(CCAT, x) for x in os.listdir(CCAT) if x.endswith('.pickle')]
files.append(NT)

file_pattern = files[0].split('_')
word = file_pattern[0]
if 'CS' in file_pattern[-1]:
    default_val = 1
elif 'LL' in file_pattern[-1]:
    default_val = 0

def extract_info(f):
    df = pd.read_pickle(f)
    return df.ix['ἐκκλησία'].fillna(0), df.index
    

#this is the dictionary with the words and categories of the Louw-Nida lexicon
LN = pd.read_pickle(LN_file)

for file in files:
    s, df_index = extract_info(file)
    cat_sum = pd.Series(0, index = range(1, len(LN)+1))
    for cat in LN:
        cat_count = 0
        for word in LN[cat]['Words']:
            if word in df_index:
                cat_count += 1
                cat_sum.ix[cat] += s.ix[word]
        if cat_count > 0:
            cat_sum.ix[cat] /= cat_count
        else:
            cat_sum.ix[cat] = default_val
    dest_file = os.path.join(dest, ''.join(['ἐκκλησία_', os.path.split(file)[-1]]))
    cat_sum.to_pickle(dest_file)
                
