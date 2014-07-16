'''
The purpose of this script is to extract the CS scores of all words that occur
at least 50x in each pair of biblical corpora.
'''

import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
import os
import datetime

orig = askdirectory(title = 'Where are your CS compared pickles located?')
CCAT_lems = askdirectory(title = 'Where are your CCAT lem dicts?')
NT_lem = askopenfilename(title = 'Where is your NT lem dict?')
dest = askdirectory(title = 'Where would you like to save your resulting files?')

files = [x for x in os.listdir(orig) if x.endswith('.pickle')]
lems = [os.path.join(CCAT_lems, x) for x in os.listdir(CCAT_lems) if x.endswith('.pickle')]
lems.append(NT_lem)
lems_dict = {}
for lem in lems:
    corpus = os.path.split(lem)[1].split('_')[0]
    lems_dict[corpus] = lem

for filename in files:
    corp_1 = filename.split('_')[0]
    corp_2 = filename.split('_')[1]
    print('Comparing %s and %s at %s' % (corp_1, corp_2, datetime.datetime.now().time().isoformat()))
    s = pd.read_pickle(os.path.join(orig, filename))
    dict_1 = pd.read_pickle(lems_dict[corp_1])
    dict_2 = pd.read_pickle(lems_dict[corp_2])
    df_50 = pd.DataFrame(columns = ('Cosine Distance', ''.join([corp_1, ' occurrences']), ''.join([corp_2, ' occurrences'])))
    for word, value in s.iteritems():
        try:
            if dict_1[word] >= 50 and dict_2[word] >= 50:
                df_50.ix[word] = (value, dict_1[word], dict_2[word])
        except:
            continue
    dest_file = os.path.join(dest, '_'.join([corp_1, corp_2, '50x_CS.pickle']))
    dest_csv = os.path.join(dest, '_'.join([corp_1, corp_2, '50x_CS.csv']))
    df_50.to_pickle(dest_file)
    df_50.to_csv(dest_csv)
