__author__ = 'matt'

import pandas as pd
import numpy as np
import os.path
import sys
from pickle import dump

sys.setrecursionlimit(50000)

#word_cats = (('θεός', 12), ('ἔθνος', 11), ('λατρεύω', 53),
#             ('βασιλεύς', 37), ('ἡγέομαι', 36), ('γινώσκω', 28))

ln = pd.read_pickle('/media/matt/Github/Diss_Data/LouwNidaDict.pickle')
scores = {}
averages = {}

for win in (20, 60, 100, 200, 300, 400, 500):
	scores[win] = {}
	file = os.path.join('/media/matt/Github/Diss_Data/SBLGNT/CS',
						str(win), 'SBL_GNT_text_PMICS.pickle')
	df = pd.read_pickle(file)
	mean, std = np.mean(df.values), np.std(df.values)
	print('%s average: %s, std: %s' % (win, mean, std))
	for cat in ln.keys():
		scores[win][cat] = pd.DataFrame(index=ln[cat]['Words'],
										columns=['Mean', 'STD +/-'])
		for word1 in ln[cat]['Words']:
			vals = []
			for word2 in ln[cat]['Words']:
				if word1 != word2:
					try:
						vals.append(df.ix[word1, word2])
					except KeyError as E:
						continue
			scores[win][cat].ix[word1, 'Mean'] = np.mean(vals)
			scores[win][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
	total = 0
	for cat in scores[win]:
		total += scores[win][cat].sum()
	averages[win] = total/93
dump(scores, open('/media/matt/Github/Diss_Data/LN_Word_Cat_Scores.pickle',
				  mode='wb'))
dump(averages, open('/media/matt/Github/Diss_Data/LN_Window_Averages.pickle',
					mode='wb'))

