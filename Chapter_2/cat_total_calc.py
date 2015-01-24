__author__ = 'matt'

import pandas as pd
import numpy as np

def CatCalc(metric='Ave STD +/-'):
	cats = pd.read_pickle('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle')
	lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
	aves = pd.read_csv('Data/Chapter_2/Average_Similary_by_Word_Frequency.csv',
					   index_col=0)
	d = aves.ix[:, metric]
	metric2 = metric.lstrip('Ave ')

	with open('Data/Chapter_2/Cat_Ave_CS.csv', mode='w', encoding='utf-8') as f:
		for cat in cats[1.45]:
			cat_total = []
			for word in cats[1.45][cat].index:
				try:
					cat_total.append(cats[1.45][cat].ix[word, metric2] - d[min((lems[word[0]]['count']//10)*10, 200)])
				except KeyError:
					print(word)
					continue
			f.write('{0}\t{1}\n'.format(cat, np.mean(cat_total)))