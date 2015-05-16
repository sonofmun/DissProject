#! /usr/bin/env python3

__author__ = 'matt'

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


import re
from collections import defaultdict, Counter
import datetime
from math import log, ceil, pow

import pandas as pd
import numpy as np

try:
	from tkinter.filedialog import askdirectory
except ImportError:
	print('Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')
from sklearn.metrics.pairwise import pairwise_distances
from glob import glob
from celery import group
from proj.tasks import counter
from sklearn.cross_validation import KFold
from pickle import dump
from copy import deepcopy
import os


class SemPipeline:

	def __init__(self, win_size=350, lemmata=True, weighted=True, algo='PPMI', svd=1.45, files=None, c=8):
		"""
		"""
		self.w = win_size
		self.lems = lemmata
		self.weighted = weighted
		self.algo = algo
		self.svd = svd
		self.dir = files
		self.c = c


	def file_chooser(self):
		if self.dir == None:
			title = 'In which directory are the XML file(s) would you like to analyze?'
			self.dir = askdirectory(title=title)

	def df_to_hdf(self, df, dest):
		df.to_hdf(dest, 'df', mode='w', complevel=9, complib='blosc')

	def word_extract(self):
		'''
		Extracts all of the words/lemmata from the lines extracted from
		the XML file
		'''
		if self.lems:
			return [re.sub(r'.+?lem="([^"]*).*', r'\1', line).lower()
					 for line in self.t]
		else:
			return [re.sub(r'.+?>([^<]*).*', r'\1', line).lower()
					 for line in self.t]


	def cooc_counter(self):
		'''
		This function takes a token list, a windows size (default
		is 4 left and 4 right), and a destination filename, runs through the
		token list, reading every word to the window left and window right of
		the target word, and then keeps track of these co-occurrences in a
		cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
		this dictionary and then pickles this DataFrame to dest
		'''
		#self.coll_df = pd.DataFrame()
		cooc_dest = os.path.join(self.dest,
								 '_'.join(['COOC',
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   self.corpus]) + '.hd5')
		if os.path.isfile(cooc_dest):
			self.coll_df = pd.read_hdf(cooc_dest, 'df')
			return
		counts = Counter()
		for file in glob('{0}/*.txt'.format(self.dir)):
			with open(file) as f:
				self.t = f.read().split('\n')
			#print('Now analyzing {0}'.format(file))
			words = self.word_extract()
			step = ceil(len(words)/self.c)
			steps = []
			for i in range(self.c):
				steps.append((step*i, min(step*(i+1), len(words))))
			self.res = group(counter.s(self.weighted, self.w, words, limits) for limits in steps)().get()
			for r in self.res:
				for key in r.keys():
					if key in counts.keys():
						counts[key].update(r[key])
					else:
						counts[key] = r[key]
		#self.coll_df = pd.DataFrame(0, index=list(counts.keys()), columns=list(counts.keys()))
		#for key in counts.keys():
		#	for key2 in counts[key].keys():
		#		self.coll_df.ix[key, key2] = counts[key][key2]
		self.coll_df = pd.DataFrame(counts, dtype=np.float32).fillna(0)
		print('Now writing cooccurrence file at {0}'.format(datetime.datetime.now().time().isoformat()))
		try:
			self.df_to_hdf(self.coll_df, cooc_dest)
		except AttributeError:
			print('Cooccurrence calculation finished')

	def log_L(self, k, n, x):
		'''
		This function applies the correct values from the DataFrame to the
		binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
		'''
		return np.log(np.power(np.float64(x),k)
					  * np.power(np.float64(1-x),n-k))

	def log_space_L(self, k, n, x):
		'''
		This function finds all the inf and -inf values in the Series s and
		corrects the NaN and inf values by moving the whole equation to the log
		space, so that ln((x**k)*(1-x)**(n-k)) = (ln(x)*k) + (ln(1-x)*(n-k))
		I use math.log here instead of np.log because all the values are
		scalars instead of Series and math.log is 10x faster than np.log
		'''
		return np.log(x) * (k) + (np.log(1-x) * (n-k))

	def log_like(self, row, C2, P, N):
		'''
		values for c12
		this is the row in the coll_df that I am looking at
		'''
		C12 = self.coll_df.ix[row]
		#value for C1 will be a scalar value used for all calculations on
		#that row
		C1 = np.sum(C12)
		#The values for P1 and P2 will be the same for the whole row
		#P1, P2 = p_calc(C1, C2, C12, N)
		P1 = C12/C1
		#values for p2
		P2 = (C2-C12)/(N-C1)

		'''
		The following lines call alternately the log_L and the log_space_L
		function.  The first will calculate most values correctly except where
		they underrun the np.float128 object (10**-4950).  Those cases will be
		dealt with by moving the calculations to log space, thus calculating
		the natural log before the float128 can be underrun when taking a
		very small P number to even a moderately large exponent.
		I have only seen this occur in calculating LL3 and LL4, so I have
		commented the calls to log_L for LL1 and LL2 out.  Uncomment and use
		them if you experience np.float128 underrun on your data.
		'''

		LL1 = self.log_space_L(C12, C1, P)

		'''
		The following finds all inf and -inf values in LL1 by
		moving calculations into log space.
		'''
		'''
		LL1_inf = LL1[np.isinf(LL1)]
		for ind in LL1_inf.index:
			try:
				LL1.ix[ind] = (log(P[ind])*C12[ind])+\
							  (log(1-P[ind])*(C1-C12[ind]))
			except ValueError as E:
				LL1.ix[ind] = 0
		'''
		LL2 = self.log_space_L(C2-C12, N-C1, P)


		'''
		The following finds all inf and -inf values in LL2 by
		moving calculations into log space.
		'''
		'''
		LL2_inf = LL2[np.isinf(LL2)]
		for ind in LL2_inf.index:
			try:
				LL2.ix[ind] = (log(P[ind])*(C2[ind]-C12[ind]))+\
							  (log(1-P[ind])*((N-C1)-(C2[ind]-C12[ind])))
			except ValueError as E:
				LL2.ix[ind] = 0
		'''
		LL3 = self.log_L(C12, C1, P1)

		'''
		The following finds all inf and -inf values in LL3 by
		moving calculations into log space.
		'''

		LL3_inf = LL3[np.isinf(LL3)]
		for ind in LL3_inf.index:
			try:
				LL3.ix[ind] = (log(P1[ind])*C12[ind])+\
							  (log(1-P1[ind])*(C1-C12[ind]))
			except ValueError as E:
				LL3.ix[ind] = 0

		LL4 = self.log_space_L(C2-C12, N-C1, P2)

		'''
		The following finds all inf and -inf values in LL4 by
		moving calculations into log space.
		'''

		LL4_inf = LL4[np.isinf(LL4)]
		for ind in LL4_inf.index:
			try:
				LL4.ix[ind] = self.log_L((C2[ind]-C12[ind]), (N-C1), P2[ind])
			except ValueError as E:
				LL4.ix[ind] = 0
		return -2 * (LL1 + LL2 - LL3 - LL4)


	def LL(self):
		"""This function guides the log-likelihood calculation process
		"""
		dest_file = os.path.join(self.dest,
									 '_'.join(['LL',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus]) + '.hd5')
		if os.path.isfile(dest_file):
			self.stat_df = pd.read_hdf(dest_file, 'df')
			return
		n = np.sum(self.coll_df.values)
		#values for C2
		c2 = np.sum(self.coll_df)
		#values for p
		p = c2/n
		self.stat_df = pd.DataFrame(0., index=self.coll_df.index,
							 columns=self.coll_df.index, dtype=np.float32)
		for row in self.coll_df.index:
			self.stat_df.ix[row] = self.log_like(row, c2, p, n)
		self.stat_df = self.stat_df.fillna(0)
		try:
			self.df_to_hdf(self.stat_df, dest_file)
			del self.coll_df
		except AttributeError:
			print('LL calc finished')

	def PMI_calc(self, row, P2, N):
		'''
		values for c12
		this is the row in the coll_df that I am looking at
		'''
		C12 = self.coll_df.ix[row]
		#value for C1 will be a scalar value used for all calculations on
		#that row
		C1 = np.sum(C12)
		P1 = C1/N
		P12 = C12/N
		return np.log2(np.float64(np.divide(P12,P1*P2)))

	def PPMI(self):
		"""This function guides the PPMI calculation process
		"""
		dest_file = os.path.join(self.dest,
									 '_'.join(['PPMI',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus]) + '.hd5')
		if os.path.isfile(dest_file):
			self.stat_df = pd.read_hdf(dest_file, 'df')
			return
		n = np.sum(self.coll_df.values)
		#values for C2
		p2 = np.sum(self.coll_df)/n
		self.stat_df = pd.DataFrame(0., index=self.coll_df.index,
							 columns=self.coll_df.index, dtype=np.float32)
		for row in self.coll_df.index:
			self.stat_df.ix[row] = self.PMI_calc(row, p2, n)
		self.stat_df[self.stat_df<0] = 0
		self.stat_df= self.stat_df.fillna(0)
		try:
			self.df_to_hdf(self.stat_df, dest_file)
			del self.coll_df
		except AttributeError:
			print('PPMI Calc finished')

	def CS(self):
		"""This function calls the pairwise distance function from sklearn
		on every log-likelihood DataFrame in a certain directory and returns
		the similarity score (i.e., 1-cosine distance) for every word, saving
		the results then to a different directory.
		"""
		print('Starting CS calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))
		self.stat_df = self.stat_df.replace(to_replace=np.inf, value=0)
		if __name__ == '__main__':
			CS_Dists = 1-pairwise_distances(self.stat_df, metric='cosine', n_jobs=-1)
		else:
			CS_Dists = 1-pairwise_distances(self.stat_df, metric='cosine', n_jobs=1)
		self.CS_df = pd.DataFrame(CS_Dists, index=self.stat_df.index,
								  columns=self.stat_df.index, dtype=np.float32)
		try:
			dest_file = os.path.join(self.dest,
									 '_'.join([self.algo,
											   'CS',
											   str(self.w),
											   self.corpus,
											   'lems={0}'.format(self.lems),
											   'SVD_exp={0}.hd5'.format(str(self.svd))]))
			self.df_to_hdf(self.CS_df, dest_file)
			del self.stat_df
		except AttributeError:
			print('Not saving CS file')
		print('Finished with CS calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))

	def stat_eval(self):
		print('Starting %s calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.algo,
				   self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))
		try:
			assert(self.algo == 'PPMI')
			self.PPMI()
		except AssertionError as E:
			self.LL()
		print('Finished with %s calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.algo,
				   self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))

	def svd_calc(self):
		"""Calculates the truncated singular value decomposition of df
		using the first n principal components

		:param df:
		"""
		print('Starting SVD calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))
		from scipy import linalg
		U, s, Vh = linalg.svd(self.stat_df)
		S = np.diag(s)
		self.stat_df = pd.DataFrame(np.dot(U, S**self.svd),
					 index=self.stat_df.index)
		print('Finished SVD calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))

	def makeFileNames(self):
		self.dest = os.path.join(self.dir, str(self.w))
		try:
			os.mkdir(self.dest)
		except:
			pass
		self.corpus = '_'.join(self.dir.split('/')[-1].split('_')[:-1])

	def runPipeline(self):
		if self.dir == None:
			self.file_chooser()
		self.makeFileNames()
		print('Started analyzing %s at %s' %
			  (self.corpus,
			   datetime.datetime.now().time().isoformat()))
		self.cooc_counter()
		self.stat_eval()
		if self.svd != 1:
			self.svd_calc()
		self.CS()

		print('Finished at %s' % (datetime.datetime.now().time().isoformat()))

class PseudoLem(SemPipeline):

	def __init__(self, win_size=350, lemmata=False, weighted=True, algo='PPMI', svd=1.45, files=None, forms=[], lemma=''):
		"""
		"""
		self.w = win_size
		self.lems = lemmata
		self.weighted = weighted
		self.algo = algo
		self.svd = svd
		self.dir = files
		self.forms = forms
		self.lemma = lemma

	def makeFileNames(self):
		filename = '_'.join(self.dir.split('_')[:-1])
		self.dest = os.path.join(self.dir, str(self.w), self.lemma)
		try:
			os.mkdir(self.dest)
		except:
			pass
		self.corpus = filename.split('_')[-3:-1]

	def cooc_counter(self):
		'''
		This function takes a token list, a windows size (default
		is 4 left and 4 right), and a destination filename, runs through the
		token list, reading every word to the window left and window right of
		the target word, and then keeps track of these co-occurrences in a
		cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
		this dictionary and then pickles this DataFrame to dest
		'''
		self.dest = os.path.join(self.dest, self.lemma)
		words = self.word_extract()
		for i, word in enumerate(words):
			if word in self.forms:
				words[i] = self.lemma
		cooc_dict = defaultdict(dict)
		for i, t in enumerate(words):
			c_list = []
			if self.weighted:
				for pos in range(max(i-self.w, 0),min(i+self.w+1, len(words))):
					if pos != i:
						for x in range(self.w+1-abs(i-pos)):
							c_list.append(words[pos])
			else:
				[c_list.append(c) for c in
				 words[max(i-self.w, 0):min(i+self.w+1, len(words))]]
				c_list.remove(t)
			for c in c_list:
				try:
					cooc_dict[t][c] += 1
				except KeyError:
					cooc_dict[t][c] = 1
			if i % 100000 == 0:
				print('Processing token %s of %s at %s' % (i, len(words),
								datetime.datetime.now().time().isoformat()))
		self.coll_df = pd.DataFrame(cooc_dict).fillna(0)
		dest_file = os.path.join(self.dest,
								 '_'.join(['COOC',
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   self.corpus[0],
										   self.corpus[1]]) + '.hd5')
		self.coll_df.to_hdf(dest_file, 'df', mode='w', complevel=9, complib='blosc')

class WithCelery(SemPipeline):

	def cooc_counter(self):
		'''
		This function takes a token list, a windows size (default
		is 4 left and 4 right), and a destination filename, runs through the
		token list, reading every word to the window left and window right of
		the target word, and then keeps track of these co-occurrences in a
		cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
		this dictionary and then pickles this DataFrame to dest
		'''
		words = self.word_extract()
		vocab = list(set(words))
		self.coll_df = pd.DataFrame(index=vocab, columns=vocab)
		c = 8
		step = ceil(len(words)/c)
		steps = []
		for i in range(c):
			steps.append((step*i, min(step*(i+1), len(words))))
		res = group(counter.s(self.weighted, self.w, words, limits) for limits in steps)().get()
		for r in res:
			self.coll_df = self.coll_df.add(pd.DataFrame(r), fill_value=0)
		self.coll_df.fillna(0)
		dest_file = os.path.join(self.dest, 'test',
								 '_'.join(['COOC',
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   self.corpus[0],
										   self.corpus[1]]) + '.hd5')
		self.coll_df.to_hdf(dest_file, 'df', mode='w', complevel=9, complib='blosc')

class ParamTester(SemPipeline):

	def __init__(self, c=8):
		"""
		"""
		self.c = c

	def cooc_counter(self, text):
		'''
		This function takes a token list, a windows size (default
		is 4 left and 4 right), and a destination filename, runs through the
		token list, reading every word to the window left and window right of
		the target word, and then keeps track of these co-occurrences in a
		cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
		this dictionary and then pickles this DataFrame to dest
		'''
		coll_df = pd.DataFrame()
		self.t = text
		words = self.word_extract()
		step = ceil(len(words)/self.c)
		steps = []
		for i in range(self.c):
			steps.append((step*i, min(step*(i+1), len(words))))
		res = group(counter.s(self.weighted, self.w, words, limits) for limits in steps)().get()
		for r in res:
			coll_df = coll_df.add(pd.DataFrame(r), fill_value=0)
		coll_df = coll_df.fillna(0)
		return coll_df

	def scaler(self, df):
		"""Scales the values of the given DataFrame to a range between
		0 and 1

		:param df:
		"""
		from sklearn.preprocessing import MinMaxScaler
		df1 = deepcopy(df)
		scaled = pd.DataFrame(MinMaxScaler
							  (feature_range=(.01,1)).fit_transform(df1),
							  index = df.index,
							  columns = df.columns,
							  dtype=np.float128)
		return scaled

	def RunTests(self, min_w, max_w, step, orig=None):

		self.perplex_dict = {}
		files = glob('{0}/*.txt'.format(orig))
		folds = defaultdict(list)
		#calculate the fold indices for all of the individual text
		for file in files:
			with open(file, mode='r', encoding='utf-8') as f:
				t = f.read().split('\n')
			kf = KFold(len(t), n_folds=10)
			for train, test in kf:
				t_train = [t[i] for i in train]
				t_test = [t[i] for i in test]
				folds[file].append([t_train, t_test])
		for self.w in range(min_w, max_w+1, step):
			self.coll_df = pd.DataFrame()
			t_test = pd.DataFrame()
			self.weighted = True
			self.lems = True
			ll_list = []
			pmi_list = []
			counter = 1
			#this loop goes through each of the 10 folds for each text
			#it will keep track of the test and train cooccurrence statistics
			#individually
			for f_num in range(10):
				print('Fold %s, weighted %s, lemmata %s, w=%s at %s' %
					  (f_num,
					   self.weighted,
					   self.lems,
					   self.w,
					   datetime.datetime.now().time().isoformat()))

				for file in folds.keys():
					self.coll_df = self.coll_df.add(self.cooc_counter(folds[file][f_num][0]), fill_value=0).fillna(0)
					t_test = t_test.add(self.cooc_counter(folds[file][f_num][1]), fill_value=0).fillna(0)
				#laplace smoothing
				self.coll_df = self.coll_df + 1
				t_test = t_test + 1
				ind_int = set(self.coll_df.index).intersection(t_test.index)
				exponent = 1/np.sum(t_test.values)
				print('Starting LL calculations for '
					  'window size %s at %s' %
					  (str(self.w),
					   datetime.datetime.now().time().isoformat()))
				self.LL()
				ll_list.append(pow
							   (np.e,
								np.sum
								(np.log(1/np.multiply(self.scaler(self.stat_df).ix[ind_int,ind_int],
													  t_test.ix[ind_int,ind_int]).values))
								* exponent))
				del self.stat_df
				print('Starting PPMI calculations for '
					  'window size %s at %s' %
					  (str(self.w),
					  datetime.datetime.now().time().isoformat()))
				self.PPMI()
				pmi_list.append(pow
								(np.e, np.sum(np.log(1/np.multiply(self.scaler(self.stat_df).ix[ind_int,ind_int],
									 t_test.ix[ind_int,ind_int]).values))
								* exponent))
				#del self.stat_df
				counter += 1
			self.perplex_dict[('LL',
						  self.w,
						  'lems=%s' % (self.lems),
						  'weighted =%s' % (self.weighted))] = \
							sum(ll_list)/len(ll_list)
			self.perplex_dict[('PPMI',
						  self.w,
						  'lems=%s' % (self.lems),
						  'weighted =%s' % (self.weighted))] = \
							sum(pmi_list)/len(pmi_list)
		dest_file = '{0}/{1}_{2}_perplexity.pickle'.format(orig, min_w, max_w)
		with open(dest_file, mode='wb') as f:
			dump(self.perplex_dict, f)


if __name__ == '__main__':
	if sys.argv[1] == "SemPipeLine":
		SemPipeline(win_size=int(sys.argv[2]),
				lemmata=bool(int(sys.argv[3])),
				weighted=bool(int(sys.argv[4])),
				algo=sys.argv[5],
				svd=float(sys.argv[6]),
				files=sys.argv[7],
				c=int(sys.argv[8])).runPipeline()
	if sys.argv[1] == "ParamTester":
		ParamTester(c=int(sys.argv[2])).RunTests(min_w=int(sys.argv[3]),
												 max_w=int(sys.argv[4]),
												 step=int(sys.argv[5]),
												 orig=sys.argv[6])