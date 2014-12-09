    '''
This script extracts the words for specific domains in the LouwNida lexicon and plots their relationship among the different
corpora.
'''

import pandas as pd
import numpy as np
import os
from tkinter.filedialog import askdirectory, askopenfilenames, askopenfilename
import matplotlib.pyplot as plt

CCAT = askopenfilenames(title = 'Which CCAT pickles would you like to use?')
NT = askopenfilename(title = 'Where is your NT data pickle?')
LN_file = askopenfilename(title = 'Where is your LouwNida dictionary?')

corpora = {}
corp_names = {'LXX': 'Septuagint', 'PE': 'Pentateuch', 'FP': 'Former Prophets', 'LP': 'Later Prophets',
              'WR': 'Writings', 'IN': 'Intertestamental', 'GNT': 'New Testament'}
target = 'ἐκκλησία'

if 'CS' in CCAT[0]:
    default = 1
    method = 'Cosine Distance'
else:
    default = 0
    method = 'Log-likelihood'
for file in CCAT:
    corp = (os.path.split(file)[1]).split('_')[0]
    corpora[corp_names[corp]] = pd.read_pickle(file)

corpora['New Testament'] = pd.read_pickle(NT)
domain = 56

LN = pd.read_pickle(LN_file)
words = LN[domain]['Words']
df = pd.DataFrame(index = corpora.keys(), columns = words)
for corpus in corpora.keys():
    for word in words:
        if word in corpora[corpus].ix[target].index:
            df.ix[corpus, word] = corpora[corpus].ix[target, word]
        else:
            df.ix[corpus, word] = np.nan
df = df.dropna(axis = 1, how = 'all')
df = df.fillna(default)
ax = plt.axes()
ax.set_title('%s Comparison of Words in "%s" Domain' % (method, LN[domain]['Gloss']), fontsize = 24)
counter = 0
lines = ['k', 'k--', 'k-.', 'k:', 'ko', 'ks']
for corpus in corpora.keys():
    ax.plot(df.ix[corpus], lines[counter], label = corpus)
    counter += 1
ax.set_xticks(range(len(df.columns)))
ax.set_xticklabels(df.columns, rotation = 85, size = 'x-large')
ax.legend(fontsize = 'x-large')
ax.grid()
plt.show()





    
