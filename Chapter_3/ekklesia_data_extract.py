__author__ = 'matt'

import pandas as pd

def extract(words=['ἐκκλησίᾳ', 'ἐκκλησιῶν', 'ἐκκλησίαι', 'ἐκκλησία', 'ἐκκλησίαν', 'ἐκκλησίαις', 'ἐκκλησίας'], source='/media/matt/Data/DissProject/Data/350/PPMI_CS_350_lems=False_SBL_GNT_SVD_exp=1.45.pickle'):
	df = pd.read_pickle(source)
	for word in words:
		dest = '/media/matt/Data/DissProject/Data/Chapter_3/{0}.txt'.format(word)
		df.ix[word, :].order(ascending=False).head(60).to_csv(dest)