__author__ = 'matt'

import pandas as pd

cats = pd.read_pickle('../Data/Chapter_2/LN_Cat_Dict.pickle')
lems = pd.read_pickle('../Data/SBLGNT_lem_dict.pickle')
scores = pd.read_csv('../Data/Chapter_2/Cat_Ave_CS.csv',
					 header=None, sep='\t', index_col=0)

with open('../Data/Chapter_2/Good_Cats.txt', mode='w', encoding='utf-8') as f:
	for cat in cats.keys():
		gt_20 = 0
		try:
			for word in cats[cat]['words']:
				if lems[list(word.keys())[0]]['count'] >= 20:
					gt_20 += 1
		except KeyError:
			continue
		if gt_20 * 2 >= len(cats[cat]['words']):
			f.write('{0}\t{1}\n'.format(cat, scores.ix[str(cat), 1]))