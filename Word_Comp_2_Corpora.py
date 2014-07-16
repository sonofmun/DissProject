'''
This script compares the LL or CS scores of one word between two corpora to
each other and exports it as a csv file.
'''

import pandas as pd
from tkinter.filedialog import askopenfilename, asksaveasfilename

word = input('Which Greek word would you like to investigate: ')
file1 = askopenfilename(title = 'Choose the pickle file for corpus 1')
file2 = askopenfilename(title = 'Choose the pickle file for corpus 2')
dest = asksaveasfilename(title = 'Where would you like to save the resulting csv?')

def extract_word(file):
    df = pd.read_pickle(file)
    return df.ix[word]

def const_csv(s1, s2):
    s3 = s1-s2
    s3 = s3.dropna()
    s3.sort()
    s4 = s3[:20]
    s4 = s4.append(s3[-20:])
    return s4

corpus_1 = extract_word(file1)
corpus_2 = extract_word(file2)

(const_csv(corpus_1, corpus_2)).to_csv(dest)
