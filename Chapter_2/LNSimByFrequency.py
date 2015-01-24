__author__ = 'matt'

import pandas as pd
import numpy as np

def SimByFreq(start, stop, step):
	with open('Data/Chapter_2/Average_Similary_by_Word_Frequency.csv', mode='w', encoding='utf-8') as file:
		file.write('Min Occurrences,Ave Mean,Ave STD +/-,1 STD Mean,1 STD STD,-1 STD Mean,-1 STD STD,-2 STD Mean,-2 STD STD\n')
		for m in range(start, stop, step):
			ave_scores = []
			std_scores = []
			orig = pd.read_pickle('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle')
			lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
			for cat in orig[1.45]:
				orig[1.45][cat] = orig[1.45][cat].fillna(0)
				for i in orig[1.45][cat].index:
					try:
						if lems[i[0]]['count'] >= m:
							if type(orig[1.45][cat].ix[i, 'STD +/-']) == list:
								ave_score = orig[1.45][cat].ix[i, 'STD +/-'][0]
								std_score = orig[1.45][cat].ix[i, 'Mean'][0]
							else:
								ave_score = orig[1.45][cat].ix[i, 'STD +/-']
								std_score = orig[1.45][cat].ix[i, 'Mean']
							ave_scores.append(ave_score)
							std_scores.append(std_score)
					except KeyError:
						continue
			mean = sum(std_scores)/len(std_scores)
			s = np.std(std_scores)
			ave = sum(ave_scores)/len(ave_scores)
			std = np.std(ave_scores)
			file.write('{0},{5},{1},{6},{2},{7},{3},{8},{4}\n'.format(m,
																	  ave,
																	  std,
																	  ave-std,
																	  ave-(2*std),
																	  mean,
																	  s,
																	  mean-s,
																	  mean-(2*s)))