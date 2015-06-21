__author__ = 'matt'

import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from collections import defaultdict
try:
	from Data_Production.TK_files import tk_control
except ImportError:
	print('TKinter is not available on this machine.\n Please specify your directories manually.')
import scipy.sparse
from numpy import where
from pickle import dump
import os.path
from re import sub

def calc(lex_file=None, cs_dest=None, syn_dest=None, occs_file=None, min_occs=10, stop_words=[]):
	if lex_file == None:
		try:
			lex_file = tk_control("askopenfilename(title='Where is your Moses lex file?')")
		except NameError:
			pass
	if occs_file == None:
		try:
			occs_file = tk_control("askopenfilename(title='Where is your word occurrence dictionary file?')")
		except NameError:
			pass
	with open(lex_file) as f:
		lines = f.read().split('\n')
	occs = pd.read_pickle(occs_file)
	d = defaultdict(dict)
	print('Building dictionary')
	for line in lines:
		try:
			e, g, s = line.split()
			if e not in stop_words:
				d[g][e] = s
		except ValueError:
			continue
	e_list = []
	g_list = [w for w in list(d.keys()) if occs[w] >= min_occs]
	#with open('{0}/cs_index.pickle'.format(os.path.split(cs_dest)[0]), mode='wb') as f:
	#	dump(g_list, f)
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
	CS = pd.DataFrame(1-pairwise_distances(sp_arr, metric='cosine'), index=g_list, columns=g_list)
	#CS_df = pd.DataFrame(CS, index=g_list, columns=g_list)
	if cs_dest == None:
		try:
			cs_dest = tk_control("asksaveasfilename(title='Where would you like to save your similarity data?')")
		except NameError:
			pass
	CS.to_hdf(cs_dest, 'CS', mode='w', complevel=9, complib='blosc')
	#syns = {}
	#for w in CS.index:
	#	syns[w] = dict(CS.ix[w].order(ascending=False).head(10))
	#	if occs[w] >= 10:
	#		syns[w] = dict(CS.ix[w].order(ascending=False).head(10))
	if syn_dest == None:
		try:
			syn_dest = tk_control("asksaveasfilename(title='Where would you like to save your synonym list?')")
		except NameError:
			pass
	with open(syn_dest, mode='w') as f:
		for w in CS.index:
			if occs[w] >= 10:
				#f.write('{0}\t{1}\n'.format(w, sub(r' +', r'\t', CS.ix[w].order(ascending=False).head(10).to_string().replace('\n', '\n\t'))))
				f.write('{0}\t{1}\n'.format(w, sub(r' +', r'\t', CS.ix[w, where(CS.ix[w]>.9)].order(ascending=False).to_string().replace('\n', '\n\t'))))
if __name__ == '__main__':
	print(sys.argv)
	calc(lex_file=sys.argv[1], cs_dest=sys.argv[2], syn_dest=sys.argv[3], occs_file=sys.argv[4], min_occs=int(sys.argv[5]))