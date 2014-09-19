__author__ = 'matt'

import pandas as pd
import numpy as np
import os.path

word_cats = (('θεός', 12), ('ἔθνος', 11), ('λατρεύω', 53),
             ('βασιλεύς', 37), ('ἡγέομαι', 36), ('γινώσκω', 28))

ln = pd.read_pickle('/media/matt/DATA/Diss_Data/LouwNidaDict.pickle')

for win in (20, 60, 100, 200, 300, 400, 500):
    file = os.path.join('/media/matt/DATA/Diss_Data/SBLGNT/CS',
                        str(win), 'SBL_GNT_text_PMICS.pickle')
    df = pd.read_pickle(file)
    mean, std = np.mean(df.values), np.std(df.values)
    print('%s average: %s, std: %s' % (win, mean, std))
    for word1, cat in word_cats:
        vals = []
        for word2 in ln[cat]['Words']:
            try:
                vals.append(df.ix[word1, word2])
            except KeyError as E:
                continue
        print('std ratio %s, win %s: %s' %
              (word1, win, (np.mean(vals)-mean)/std))

