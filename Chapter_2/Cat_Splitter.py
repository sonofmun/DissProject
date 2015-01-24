__author__ = 'matt'

import pandas as pd
from itertools import permutations

def Splitter(cat):
	cats = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
	cs = pd.read_pickle('Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle')
	cat_words = list(set([list(word.keys())[0] for word in cats[cat]['words']]))
	pairs = permutations(cat_words, 2)
	with open('Data/Chapter_2/{0}_word_pairs_CS.csv'.format(cat), mode='w', encoding='utf-8') as f:
		f.write('Source,Target,Weight\n')
		for w1, w2 in pairs:
			try:
				f.write('{0},{1},{2}\n'.format(w1, w2, cs.ix[w1, w2]))
			except KeyError:
				print(w1, w2)
				continue