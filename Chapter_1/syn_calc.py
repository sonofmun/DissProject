__author__ = 'matt'

import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from collections import defaultdict
from Data_Production.TK_files import tk_control

lex_file = tk_control("askopenfilename(title='Where is your Moses lex file?')")
with open(lex_file) as f:
	lines = f.read().split('\n')
d = defaultdict(dict)
for line in lines:
	try:
		e, g, s = line.split()
		d[g][e] = s
	except ValueError:
		continue
e_list = []
for key in d.keys():
	[e_list.append(w) for w in list(d[key].keys())]
e_list = list(set(e_list))
df = pd.DataFrame(index=list(d.keys()), columns=e_list)
for key in d.keys():
	for value in d[key].keys():
		df.ix[key, value] = float(d[key][value])
df = df.fillna(0)
CS = 1-pairwise_distances(df, metric='cosine')
CS_df = pd.DataFrame(CS, index=df.index, columns=df.index)
dest_file = tk_control("asksaveasfilename(title='Where would you like to save for similarity data?')")
CS_df.to_hdf(dest_file, 'CS', mode='w', complevel=9, complib='blosc')