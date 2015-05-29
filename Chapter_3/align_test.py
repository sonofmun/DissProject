__author__ = 'matt'

import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
from Data_Production.TK_files import tk_control
from collections import Counter
import scipy.sparse
from numpy import save
from sklearn.feature_extraction.text import TfidfTransformer

class align():

	def __init__(self, tfidf=True):
		self.tfidf = tfidf

	def load_txt(self):
		trans_file = tk_control("askopenfilename(title='Where is your hand translation?')")
		moses_file = tk_control("askopenfilename(title='Where is your automatically translated file?')")
		self.base_name = trans_file.replace('.en', '')
		with open(trans_file) as f:
			trans_text = f.read()
		with open(moses_file) as f:
			moses_text = f.read()
		self.trans_sents = trans_text.split('\n')
		self.moses_sents = moses_text.split('\n')
		trans_words = set(trans_text.split())
		moses_words = set(moses_text.split())
		self.union_words = trans_words.union(moses_words)

	def build_arrays(self):
		d = {}
		for i, sent in enumerate(self.trans_sents):
			d[i] = Counter(sent.split())
		self.trans_arr = scipy.sparse.csr_matrix(pd.DataFrame(d,
														 index=self.union_words,
														 columns=d.keys()).fillna(0).T)
		if self.tfidf:
			self.trans_arr = TfidfTransformer().fit_transform(self.trans_arr)
			save('{0}_trans_array_tfidf'.format(self.base_name), self.trans_arr)
		else:
			save('{0}_trans_array'.format(self.base_name), self.trans_arr)
		d = {}
		for i, sent in enumerate(self.moses_sents):
			d[i] = Counter(sent.split())
		self.moses_arr = scipy.sparse.csr_matrix(pd.DataFrame(d,
														 index=self.union_words,
														 columns=d.keys()).fillna(0).T)
		if self.tfidf:
			self.moses_arr = TfidfTransformer().fit_transform(self.moses_arr)
			save('{0}_moses_array_tfidf'.format(self.base_name), self.moses_arr)
		else:
			save('{0}_moses_array'.format(self.base_name), self.moses_arr)

	def sim_calc(self, algorithm):
		sim_df = pd.DataFrame(pairwise_distances(self.trans_arr, self.moses_arr, metric=algorithm))
		sim_df.to_hdf(self.dest_file, algorithm)
		matches = 0
		for x in sim_df.index:
			if sim_df.ix[x].idxmin() == x:
				matches += 1
		return matches, sim_df.shape[0]

	def pipe(self):
		self.dest_file = tk_control("asksaveasfilename(title='Where would you like to save your h5 file?')")
		results_file = tk_control("asksaveasfilename(title='Where would you like to save your results?')")
		self.load_txt()
		self.build_arrays()
		algos = ['cityblock', 'cosine', 'euclidean', 'l1', 'l2', 'manhattan']
		with open(results_file, mode='w') as f:
			f.write('Algorithm,# of Matches,Total Sentences,Accuracy\n')
			for algo in algos:
				print('Now calculating {0} distance'.format(algo))
				match, total = self.sim_calc(algo)
				f.write('{0},{1},{2},{3}\n'.format(algo, match, total, match/total))