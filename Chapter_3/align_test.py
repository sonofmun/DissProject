__author__ = 'matt'

import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
try:
	from Data_Production.TK_files import tk_control
except ImportError:
	print('Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')
from collections import Counter
import scipy.sparse
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer

class align():

	def __init__(self, corpus, tfidf=True, trans_file=None, moses_file=None, dest_dir=None):
		self.tfidf = tfidf
		self.trans_file = trans_file
		self.moses_file = moses_file
		self.dest_dir = dest_dir
		self.corpus = corpus

	def load_txt(self):
		if self.trans_file == None:
			self.trans_file = tk_control("askopenfilename(title='Where is your hand translation?')")
		if self.moses_file == None:
			self.moses_file = tk_control("askopenfilename(title='Where is your automatically translated file?')")
		self.base_name = self.trans_file.replace('.en', '')
		with open(self.trans_file) as f:
			trans_text = f.read()
		with open(self.moses_file) as f:
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
			np.save('{0}_trans_array_tfidf'.format(self.base_name), self.trans_arr)
		else:
			np.save('{0}_trans_array'.format(self.base_name), self.trans_arr)
		d = {}
		for i, sent in enumerate(self.moses_sents):
			d[i] = Counter(sent.split())
		self.moses_arr = scipy.sparse.csr_matrix(pd.DataFrame(d,
														 index=self.union_words,
														 columns=d.keys()).fillna(0).T)
		if self.tfidf:
			self.moses_arr = TfidfTransformer().fit_transform(self.moses_arr)
			np.save('{0}_moses_array_tfidf'.format(self.base_name), self.moses_arr)
		else:
			np.save('{0}_moses_array'.format(self.base_name), self.moses_arr)

	def sim_calc(self, algorithm):
		sim_df = pd.DataFrame(pairwise_distances(self.trans_arr, self.moses_arr, metric=algorithm))
		sim_df.to_hdf(self.dest_file, algorithm)
		matches = 0
		for x in sim_df.columns:
			if sim_df.ix[max(x-50, 0):min(x+50, len(sim_df.columns)), x].idxmin() == x:
				matches += 1
			#if sim_df.ix[:, x].idxmin() == x:
			#	matches += 1
		return matches, sim_df.shape[0]

	def pipe(self):
		if self.dest_dir == None:
			self.dest_file = tk_control("asksaveasfilename(title='Where would you like to save your h5 file?')")
		else:
			self.dest_file = '{0}/{1}_align_sim_dfs_tfidf={2}.h5'.format(self.dest_dir, self.corpus, self.tfidf)
		results_file = self.dest_file.replace('.h5', '.csv')
		self.load_txt()
		self.build_arrays()
		algos = ['cityblock', 'cosine', 'euclidean', 'l1', 'l2', 'manhattan']
		with open(results_file, mode='w') as f:
			f.write('Algorithm,# of Matches,Total Sentences,Accuracy\n')
			for algo in algos:
				print('Now calculating {0} distance'.format(algo))
				match, total = self.sim_calc(algo)
				f.write('{0},{1},{2},{3}\n'.format(algo, match, total, match/total))
		print('Finished')

class print_aligned(align):

	def load_txt(self):
		trans_file = tk_control("askopenfilename(title='Where is your hand translation?')")
		moses_file = tk_control("askopenfilename(title='Where is your automatically translated file?')")
		orig_lang = tk_control("askopenfilename(title='Where is your original language file?')")
		self.base_name = trans_file.replace('.en', '')
		with open(trans_file) as f:
			trans_text = f.read()
		with open(moses_file) as f:
			moses_text = f.read()
		with open(orig_lang) as f:
			self.orig_sents = f.read().split('\n')
		self.trans_sents = trans_text.split('\n')
		self.moses_sents = moses_text.split('\n')
		trans_words = set(trans_text.split())
		moses_words = set(moses_text.split())
		self.union_words = trans_words.union(moses_words)

	def sim_calc(self, algorithm):
		sim_df = pd.DataFrame(pairwise_distances(self.trans_arr, self.moses_arr, metric=algorithm))
		sim_df.to_hdf(self.dest_file, algorithm)
		matches = []
		ratio = len(sim_df.columns)/len(sim_df.index)
		if ratio < 1:
			ratio = 1/ratio
		for x in sim_df.columns:
			r = max(int(x * ratio), 20)
			m_index = sim_df.ix[max(x-r, 0):min(x+r, len(sim_df.columns)), x].idxmin()
			matches.append('Similarity={2}\n{0}\n{1}\n\n'.format(self.orig_sents[x], self.trans_sents[m_index], sim_df.ix[m_index, x]))
		return matches

	def pipe(self):
		self.dest_file = tk_control("asksaveasfilename(title='Where would you like to save your h5 file?')")
		results_file = tk_control("asksaveasfilename(title='Where would you like to save your results?')")
		self.load_txt()
		self.build_arrays()
		with open(results_file, mode='w') as f:
			print('Now calculating {0} distance'.format('CS'))
			matches = ''.join(self.sim_calc('cosine'))
			f.write(matches)

class divide_text(print_aligned):

	def find_divisions(self):
		self.first_division = np.where(self.matches.values <= np.sort(self.matches.values, axis=None)[10])

	def pipe(self):
		self.dest_file = tk_control("asksaveasfilename(title='Where would you like to save your h5 file?')")
		results_file = tk_control("asksaveasfilename(title='Where would you like to save your results?')")
		self.load_txt()
		print('Now building sparse arrays')
		self.build_arrays()
		print('Now calculating cosine distance')
		self.matches = self.sim_calc('cosine')
