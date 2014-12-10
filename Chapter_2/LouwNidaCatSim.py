__author__ = 'matt'

import pandas as pd
import numpy as np
import sys
from pickle import dump

sys.setrecursionlimit(50000)

#word_cats = (('θεός', 12), ('ἔθνος', 11), ('λατρεύω', 53),
#             ('βασιλεύς', 37), ('ἡγέομαι', 36), ('γινώσκω', 28))

ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
scores = {}
averages = {}
good_words = []
prob_words = []

for win in (20, 60, 100, 200, 300, 400, 500):
	scores[win] = {}
	file = ''.join(['Data/PMI_CS_', str(win), '_SBL_GNT.pickle'])
	df = pd.read_pickle(file)
	mean, std = np.mean(df.values), np.std(df.values)
	print('%s average: %s, std: %s' % (win, mean, std))
	tot_words = 0
	not_words = 0
	for cat in ln.keys():
		words = []
		for d in ln[cat]['words']:
			word = list(d.keys())[0]
			if word in df.index:
				words.append(word)
				tot_words += 1
				good_words.append(word)
			else:
				prob_words.append(word)
				not_words += 1
		scores[win][cat] = pd.DataFrame(index=words, columns=['Mean', 'STD +/-'])
		for word1 in words:
			vals = []
			for word2 in words:
				if word1 != word2:
					vals.append(df.ix[word1, word2])
			scores[win][cat].ix[word1, 'Mean'] = np.mean(vals)
			scores[win][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
	total = 0
	for cat in scores[win]:
		total += scores[win][cat].ix[:, 'STD +/-'].fillna(0).sum()
	averages[win] = total/tot_words
dump(scores, open('Data/Chapter_2/LN_Word_Cat_Scores.pickle', mode='wb'))
dump(averages, open('Data/Chapter_2/LN_Window_Averages.pickle', mode='wb'))
prob_words = list(set(prob_words))
good_words = list(set(good_words))
print('prob_words', len(prob_words), prob_words[:10])
print('good_words', len(good_words), good_words[:10])
print(averages)