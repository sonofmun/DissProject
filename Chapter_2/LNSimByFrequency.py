__author__ = 'matt'

import pandas as pd
import numpy as np

def SimByFreq(start, stop, step):
	with open('Data/Chapter_2/Average_Similary_by_Word_Frequency.txt', mode='w', encoding='utf-8') as file:
		for m in range(start, stop, step):
			ave_scores = []
			std_scores = []
			orig = pd.read_pickle('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle')
			lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
			for cat in orig[1.45]:
				orig[1.45][cat] = orig[1.45][cat].fillna(0)
				for i in orig[1.45][cat].index:
					if lems[i[0]]['count'] >= m:
						if type(orig[1.45][cat].ix[i, 'STD +/-']) == list:
							ave_score = orig[1.45][cat].ix[i, 'STD +/-'][0]
							std_score = orig[1.45][cat].ix[i, 'Mean'][0]
						else:
							ave_score = orig[1.45][cat].ix[i, 'STD +/-']
							std_score = orig[1.45][cat].ix[i, 'Mean']
						ave_scores.append(ave_score)
						std_scores.append(std_score)
			ave = sum(ave_scores)/len(ave_scores)
			std = np.std(ave_scores)
			file.write('{0}+ occurrences: Average STD +/- {1}, STD of STD +/- scores: {2}, -1 STD: {3}, -2 STD: {4}\n'.format(m, ave, std, ave-std, ave-(2*std)))