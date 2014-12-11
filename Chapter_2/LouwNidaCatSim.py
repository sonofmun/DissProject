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

for win in (20, 60, 100, 200, 300, 400, 500):
	scores[win] = {}
	file = ''.join(['Data/PMI_CS_', str(win), '_SBL_GNT.pickle'])
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
				words.append(word)
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
					vals.append(df.ix[word1, word2])
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
dump(scores, open('Data/Chapter_2/LN_Word_Cat_Scores.pickle', mode='wb'))
lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
for w_size in scores.keys():
	with open('Data/Chapter_2/LN_Window={0}_Word_Cat_Scores.csv'.format(w_size), mode='w', encoding='utf-8') as file:
		file.write('Scores for Window Size {0}\n'.format(w_size))
		file.write('Category,Word,# of Occurrences,Mean CS with Category,Standard Deviations +/- Average\n')
		for cat in sorted(scores[w_size].keys()):
			for index, w in enumerate(scores[w_size][cat].index):
				try:
					file.write('{0}.{1}-{2} {3},{4},{5},{6},{7}\n'.format(cat[0],
																				cat[1],
																				cat[2],
																				ln[cat]['gloss'].replace(',', ' '),
																				w,
																				lems[w]['count'],
																				scores[w_size][cat].ix[w, 'Mean'][0],
																				scores[w_size][cat].ix[w, 'STD +/-'][0]))
				except IndexError:
					file.write('{0}.{1}-{2} {3},{4},{5},{6},{7}\n'.format(cat[0],
																				cat[1],
																				cat[2],
																				ln[cat]['gloss'].replace(',', ' '),
																				w,
																				lems[w]['count'],
																				scores[w_size][cat].ix[w, 'Mean'],
																				scores[w_size][cat].ix[w, 'STD +/-']))
dump(averages, open('Data/Chapter_2/LN_Window_Averages.pickle', mode='wb'))
with open('Data/Chapter_2/LN_Window_Averages.csv', mode='w', encoding='utf-8') as file:
	file.write('Average Number of Standard Deviations above or below Average per window\n')
	file.write('Window Size,Average +/- Standard Deviations\n')
	for w_size in sorted(averages.keys()):
		file.write('{0},{1}\n'.format(w_size, averages[w_size]))
dump(ave_no_93, open('Data/Chapter_2/LN_Window_Averages_no_93.pickle', mode='wb'))
with open('Data/Chapter_2/LN_Window_Averages_no_93.csv', mode='w', encoding='utf-8') as file:
	file.write('Average Number of Standard Deviations above or below Average per window excluding LN Category 93 (Names)\n')
	file.write('Window Size,Average +/- Standard Deviations\n')
	for w_size in sorted(ave_no_93.keys()):
		file.write('{0},{1}\n'.format(w_size, ave_no_93[w_size]))
prob_words = list(set(prob_words))
good_words = list(set(good_words))
print('prob_words', len(prob_words), prob_words[:10])
print('good_words', len(good_words), good_words[:10])
print(averages, ave_no_93)