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
ave_no_93 = {}
good_words = []
prob_words = []

for win in (.1, .25, .4, .55, .7, .85, 1, 1.15, 1.3, 1.45, 1.6):#(20, 60, 100, 200, 300, 350, 400, 450, 500):
	scores[win] = {}
	file = 'Data/350/CS/PPMI_CS_350_SBL_GNT_SVD_exp={0}.pickle'.format(str(win))
	df = pd.read_pickle(file)
	mean, std = np.mean(df.values), np.std(df.values)
	print('%s average: %s, std: %s' % (win, mean, std))
	tot_words = 0
	words_no_93 = 0
	not_words = 0
	for cat in ln.keys():
		words = []
		for d in ln[cat]['words']:
			word = list(d.keys())[0]
			if word in df.index:
				words.append((word, d[word]))
				tot_words += 1
				good_words.append(word)
				if cat[0] != 93:
					words_no_93 += 1
			else:
				prob_words.append(word)
				not_words += 1
		scores[win][cat] = pd.DataFrame(index=words, columns=['Mean', 'STD +/-'])
		for word1 in words:
			vals = []
			for word2 in words:
				if word1 != word2:
					vals.append(df.ix[word1[0], word2[0]])
			#scores[win][cat].ix[word1, 'Gloss'] = word1[1]
			try:
				scores[win][cat].ix[word1, 'Mean'] = np.mean(vals)
				scores[win][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
			except ValueError:
				scores[win][cat].drop_duplicates(inplace=True)
				scores[win][cat].ix[word1, 'Mean'] = np.mean(vals)
				scores[win][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
	total = 0
	total_no_93 = 0
	for cat in scores[win]:
		total += scores[win][cat].ix[:, 'STD +/-'].fillna(0).sum()
		if cat[0] != 93:
			total_no_93 += scores[win][cat].ix[:, 'STD +/-'].fillna(0).sum()
	averages[win] = total/tot_words
	ave_no_93[win] = total_no_93/words_no_93
with open('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle', mode='wb') as file:
	dump(scores, file)
lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
for w_size in scores.keys():
	with open('Data/Chapter_2/LN_Window=350_Word_Cat_Scores_SVD_exp={0}.csv'.format(w_size),
			  mode='w', encoding='utf-8') as file:
		file.write('Scores for Window Size {0}\n'.format(w_size))
		file.write('Category,Word,Gloss,# of Occurrences,Mean CS with Category,'
				   'Standard Deviations +/- Average\n')
		for cat in sorted(scores[w_size].keys()):
			for w in scores[w_size][cat].index:
				try:
					file.write(
						'{0}.{1}-{2} {3},{4},{5},{6},{7},{8}\n'.format
						(
							cat[0],
							cat[1],
							cat[2],
							ln[cat]['gloss'].replace(',', ' '),
							w[0],
							w[1].replace(',', ' '),
							lems[w[0]]['count'],
							scores[w_size][cat].ix[w, 'Mean'][0],
							scores[w_size][cat].ix[w, 'STD +/-'][0]
						)
					)
				except IndexError:
					file.write(
						'{0}.{1}-{2} {3},{4},{5},{6},{7},{8}\n'.format
						(
							cat[0],
							cat[1],
							cat[2],
							ln[cat]['gloss'].replace(',', ' '),
							w[0],
							w[1].replace(',', ' '),
							lems[w[0]]['count'],
							scores[w_size][cat].ix[w, 'Mean'],
							scores[w_size][cat].ix[w, 'STD +/-']
						)
					)
with open('Data/Chapter_2/LN_Window_Averages_SVD.pickle', mode='wb') as file:
	dump(averages, file)
with open('Data/Chapter_2/LN_Window_Averages_SVD.csv',
		  mode='w',
		  encoding='utf-8') as file:
	file.write('Average Number of Standard Deviations above or below Average '
			   'per window\n')
	file.write('Window Size,Average +/- Standard Deviations\n')
	for w_size in sorted(averages.keys()):
		file.write('{0},{1}\n'.format(w_size, averages[w_size]))
with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.pickle', mode='wb') as file:
	dump(ave_no_93, file)
with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.csv',
		  mode='w',
		  encoding='utf-8') as file:
	file.write('Average Number of Standard Deviations above or below Average '
			   'per window excluding LN Category 93 (Names)\n')
	file.write('Window Size,Average +/- Standard Deviations\n')
	for w_size in sorted(ave_no_93.keys()):
		file.write('{0},{1}\n'.format(w_size, ave_no_93[w_size]))
prob_words = list(set(prob_words))
good_words = list(set(good_words))
print('prob_words', len(prob_words), prob_words[:10])
print('good_words', len(good_words), good_words[:10])
print(averages, ave_no_93)