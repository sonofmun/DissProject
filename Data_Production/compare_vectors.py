__author__ = 'matt'

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from itertools import combinations

class comparison:

	def __init__(self, base, english, greek, measure):
		self.corpora = [('NT', '18', 1), ('LXX', '13', 1), ('pers_data', '23', 3), ('josephus', '47', 1), ('philo', 43, 1), ('plutarch', '65', 1)]
		self.base = base
		self.ekk_rows = {}
		self.english = english
		self.greek = greek
		if measure == 'CS':
			self.prefix = 'LL_CS'
			self.svd = 'SVD_exp=1.0_'
		elif measure == 'LL':
			self.prefix = 'LL'
			self.svd = ''
		elif measure == 'cooc':
			self.prefix = 'COOC'
			self.svd = ''
		else:
			print('"measure" must be "CS", "LL", or "cooc"')

	def load_vectors(self):
		for corp in self.corpora:
			rows = pd.read_pickle('{0}{1}/{4}/{2}/{4}_IndexList_w={2}_lems=False_min_occs={3}_no_stops=False.pickle'.format(self.base, corp[0], corp[1], corp[2], self.english))
			i = rows.index(self.greek)
			r = np.memmap('{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False.dat'.format(self.base, corp[0], corp[1], corp[2], self.english, self.prefix, self.svd), dtype='float', shape=(len(rows), len(rows)))[i]
			self.ekk_rows[corp[0]] = pd.Series(r, index=rows)

	def sim_calc(self):
		self.cs_scores = pd.DataFrame(index=self.ekk_rows.keys(), columns=self.ekk_rows.keys())
		for combo in combinations(self.ekk_rows.keys(), 2):
			ekk_index = list(set(self.ekk_rows[combo[0]].index).intersection(set(self.ekk_rows[combo[1]].index)))
			self.cs_scores.ix[combo[0], combo[1]] = self.cs_scores.ix[combo[1], combo[0]] = 1 - pairwise_distances(self.ekk_rows[combo[0]][ekk_index], self.ekk_rows[combo[1]][ekk_index], metric='cosine')