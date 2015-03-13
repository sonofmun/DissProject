__author__ = 'matt'

import pandas as pd
import numpy as np

def TwoWords(w1, w2, min, orig='Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle', mult=2):
	if 'SVD' in orig:
		a = 'CS'
	elif 'PPMI' in orig:
		a = 'PPMI'
	else:
		a = 'COOC'
	l = []
	df = pd.read_pickle(orig)
	lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
	row1 = df.ix[w1]
	row2 = df.ix[w2]
	std = np.average(df.values) + (mult * np.std(df.values))
	count = 0
	for x in row1.index:
		try:
			if lems[x]['count'] >= min:
				if row1.ix[x] >= std and row2.ix[x] >= std:
					l.append([x, row1.ix[x],
							  row2.ix[x],
							  row1.ix[x] + row2.ix[x]])
					count += 1
		except KeyError:
			print(x)
			continue
	print(count)
	with open('Data/Chapter_2/{0}_{1}_Strong_Words_{2}_{3}+Occurrences.txt'.format(w1, w2, a, min), mode='w', encoding='utf-8') as f:
		f.write('Word,{2} with {0},{2} with {1},{2} Sum\n'.format(w1, w2, a))
		for item in l:
			f.write('{0},{1},{2},{3}\n'.format(item[0],
											 np.around(item[1], 4),
											 np.around(item[2], 4),
											 np.around(item[3], 4)))

def MoreWords(w1, words, min):
	l = []
	df = pd.read_pickle('Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle')
	lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
	row1 = df.ix[w1]
	std = np.average(df.values) + (2 * np.std(df.values))
	p = list(row1.index)
	for x in row1.index:
		try:
			if lems[x]['count'] >= min:
				if row1.ix[x] < std:
					p.remove(x)
					continue
				else:
					for word in words:
						if df.ix[word, x] < std:
							p.remove(x)
							break
		except KeyError:
			print(x)
			continue
	with open('Data/Chapter_2/{0}_sim_word_analysis_multi.txt'.format(w1), mode='w', encoding='utf-8') as f:
		#f.write('Word,CS with {0},CS with {1},CS Sum\n'.format(w1, w2))
		for item in p:
			f.write(str(item).strip('[]') + '\n')

def SyntagParadig(w1, w2):
	df1 = pd.read_pickle('Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle')
	df2 = pd.read_pickle('Data/350/SBL_GNT_PPMI.pickle')
	mean1 = np.mean(df1.values)
	mean2 = np.mean(df2.values)
	std1 = np.std(df1.values)
	std2 = np.std(df2.values)
	print(w1, w2, round((df1.ix[w1, w2]-mean1)/std1, 4), round((df2.ix[w1, w2]-mean2)/std2, 4))