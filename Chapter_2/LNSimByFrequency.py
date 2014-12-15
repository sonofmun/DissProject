__author__ = 'matt'

import pandas as pd

def SimByFreq(start, stop, step):
	with open('Data/Chapter_2/Average_Similary_by_Word_Frequency.txt', mode='w', encoding='utf-8') as file:
		for m in range(start, stop, step):
			scores = []
			orig = pd.read_pickle('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle')
			lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
			for cat in orig[1.45]:
				orig[1.45][cat] = orig[1.45][cat].fillna(0)
				for i in orig[1.45][cat].index:
					if lems[i[0]]['count'] >= m:
						if type(orig[1.45][cat].ix[i, 'STD +/-']) == list:
							score = orig[1.45][cat].ix[i, 'STD +/-'][0]
						else:
							score = orig[1.45][cat].ix[i, 'STD +/-']
						scores.append(score)
			ave = sum(scores)/len(scores)
			file.write('Average STD +/- for words occurring at least {0} times: {1}\n'.format(m, ave))