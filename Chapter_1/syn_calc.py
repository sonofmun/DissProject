__author__ = 'matt'

import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from collections import defaultdict
from Data_Production.TK_files import tk_control
import scipy.sparse
from numpy import save

def calc(lex_file=None, cs_dest=None, syn_dest=None):
	if lex_file == None:
		lex_file = tk_control("askopenfilename(title='Where is your Moses lex file?')")
	with open(lex_file) as f:
		lines = f.read().split('\n')
	d = defaultdict(dict)
	print('Building dictionary')
	for line in lines:
		try:
			e, g, s = line.split()
			d[g][e] = s
		except ValueError:
			continue
	e_list = []
	g_list = list(d.keys())
	for key in g_list:
		[e_list.append(w) for w in list(d[key].keys())]
	e_list = list(set(e_list))
	print('Building sparse array')
	sp_arr = scipy.sparse.lil_matrix((len(g_list), len(e_list)), dtype=float)
	for i, key in enumerate(g_list):
		for value in d[key].keys():
			sp_arr[i, e_list.index(value)] = float(d[key][value])
	sp_arr = sp_arr.tocsr()
	print('Calculating cosine similarity')
	CS = 1-pairwise_distances(sp_arr, metric='cosine')
	#CS_df = pd.DataFrame(CS, index=g_list, columns=g_list)
	if cs_dest == None:
		cs_dest = tk_control("asksaveasfilename(title='Where would you like to save your similarity data?')")
	save(cs_dest, CS)
	syns = pd.Series(sp_arr.max(axis=1).toarray(), index=g_list)
	if syn_dest == None:
		syn_dest = tk_control("asksaveasfilename(title='Where would you like to save your synonym list?')")
	syns.to_hdf(syn_dest, 'syns', mode='w', complevel=9, complib='blosc')