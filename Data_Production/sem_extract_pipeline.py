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
	from Data_Production.TK_files import tk_control
except ImportError:
	print('Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')
from sklearn.metrics.pairwise import pairwise_distances
from glob import glob
from celery import group
from proj.tasks import counter
from sklearn.cross_validation import KFold
from pickle import dump
from copy import deepcopy



class SemPipeline:

	def __init__(self, win_size=350, lemmata=True, weighted=True, algo='PPMI', svd=1.45, files=None, c=8, occ_dict=None, min_count=None, jobs=1):
		"""
		"""
		self.w = win_size
		self.lems = lemmata
		self.weighted = weighted
		self.algo = algo
		if self.algo not in ['PPMI', 'LL', 'both']:
			print('The only accepted values for "algo" are "PPMI", "LL", or "both".')
		self.svd = svd
		self.dir = files
		self.c = c
		if occ_dict == 'None':
			self.occ_dict = None
		else:
			self.occ_dict = occ_dict
		if min_count == 'None':
			self.min_count = None
		else:
			self.min_count = min_count
		self.jobs = jobs


	def file_chooser(self):
		if self.dir == None:
			self.dir = tk_control("askdirectory(title='In which directory are the XML file(s) would you like to analyze?')")

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
								 '_'.join([self.corpus,
										   'COOC',
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   self.corpus,
										   'min_occ={0}'.format(self.min_count)]) + '.dat')
		if os.path.isfile(cooc_dest):
			self.ind = pd.read_pickle('{0}/{1}_IndexList_w={2}_lems={3}.pickle'.format(self.dest, self.corpus, self.w, self.lems))
			self.coll_df = np.memmap(cooc_dest, dtype='float32', mode='r', shape=(len(self.ind), len(self.ind)))
			return
		counts = Counter()
		if self.occ_dict:
			occs = pd.read_pickle(self.occ_dict)
			min_lems = set([w for w in occs if occs[w] < self.min_count])
			del occs
		else:
			min_lems = set()
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
			#since the counter task returns Counter objects, the update method
			#below adds instead of replacing the values
			for r in self.res:
				for key in r.keys():
					if key not in min_lems:
						if key in counts.keys():
							counts[key].update(r[key])
						else:
							counts[key] = r[key]
		self.ind = list(counts.keys())
		with open('{0}/{1}_IndexList_w={2}_lems={3}.pickle'.format(self.dest, self.corpus, self.w, self.lems), mode='wb') as f:
			dump(self.ind, f)
		print('Now writing cooccurrence file at {0}'.format(datetime.datetime.now().time().isoformat()))
		self.coll_df = np.memmap(cooc_dest, dtype='float32', mode='w+', shape=(len(self.ind), len(self.ind)))
		for i, w in enumerate(self.ind):
			s = pd.Series(counts[w], index=self.ind, dtype=np.float32).fillna(0)
			self.coll_df[i] = s.values
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.coll_df
				self.coll_df = np.memmap(cooc_dest, dtype='float32', mode='r+', shape=(len(self.ind), len(self.ind)))
		del self.coll_df
		self.coll_df = np.memmap(cooc_dest, mode='r', shape=(len(self.ind), len(self.ind)))
		'''
		for (ind, key), (ind2, key2) in combinations(enumerate(self.ind), 2):
			count += 1
			self.coll_df[ind, ind2] = counts[key][key2]
			self.coll_df[ind2, ind] = counts[key2][key]
			if count % 1000 == 0:
				self.coll_df.flush()
		'''
		#self.coll_df = pd.DataFrame(counts, dtype=np.float32).fillna(0)
		#try:
		#	self.df_to_hdf(self.coll_df, cooc_dest)
		#except AttributeError:
		#	print('Cooccurrence calculation finished')

	def log_L(self, k, n, x):
		'''
		This function applies the correct values from the DataFrame to the
		binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
		'''
		return np.log(np.power(np.float32(x),k)
					  * np.power(np.float32(1-x),n-k))

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
		C12 = self.coll_df[row]
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

		LL3_inf = np.where(abs(LL3)==np.inf)
		#I need to figure out how to do this without indices
		if len(LL3_inf) > 0:
			for ind in LL3_inf[0]:
				try:
					LL3[ind] = (log(P1[ind])*C12[ind])+(log(1-P1[ind])*(C1-C12[ind]))
				except ValueError:
					LL3[ind] = 0

		LL4 = self.log_space_L(C2-C12, N-C1, P2)

		'''
		The following finds all inf and -inf values in LL4 by
		moving calculations into log space.
		'''

		LL4_inf = np.where(abs(LL4)==np.inf)
		if len(LL4_inf) > 0:
			for ind in LL4_inf[0]:
				try:
					LL4[ind] = self.log_L((C2[ind]-C12[ind]), (N-C1), P2[ind])
				except ValueError:
					LL4[ind] = 0

		a = -2 * (LL1 + LL2 - LL3 - LL4)
		a[np.where(np.isfinite(a)==False)] = 0
		return a


	def LL(self):
		"""This function guides the log-likelihood calculation process
		"""
		dest_file = os.path.join(self.dest,
									 '_'.join([self.corpus,
											   'LL',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus,
											   'min_occ={0}'.format(self.min_count)]) + '.dat')
		if os.path.isfile(dest_file):
			self.LL_df = np.memmap(dest_file, dtype='float32', mode='r', shape=(len(self.ind), len(self.ind)))
			return
		n = np.sum(self.coll_df)
		c2 = np.sum(self.coll_df, axis=1)
		p = c2/n
		self.LL_df = np.memmap(dest_file, dtype='float32', mode='w+', shape=(len(self.ind), len(self.ind)))
		for i, w in enumerate(self.ind):
			self.LL_df[i] = self.log_like(i, c2, p, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.LL_df
				self.LL_df = np.memmap(dest_file, dtype='float32', mode='r+', shape=(len(self.ind), len(self.ind)))
		self.LL_df[np.where(np.isfinite(self.LL_df)==False)] = 0
		del self.LL_df
		self.LL_df = np.memmap(dest_file, mode='r', shape=(len(self.ind), len(self.ind)))

		'''
		self.stat_df = pd.DataFrame(0., index=self.coll_df.index,
							 columns=self.coll_df.index, dtype=np.float32)
		for row in self.coll_df.index:
			self.LL_df.ix[row] = self.log_like(row, c2, p, n)
		self.LL_df = self.LL_df.fillna(0)
		try:
			self.df_to_hdf(self.LL_df, dest_file)
		except AttributeError:
			print('LL calc finished')
		'''

	def PMI_calc(self, row, P2, N):
		'''
		values for c12
		this is the row in the coll_df that I am looking at
		'''
		C12 = self.coll_df[row]
		#value for C1 will be a scalar value used for all calculations on
		#that row
		C1 = np.sum(C12)
		P1 = C1/N
		P12 = C12/N
		a = np.log2(np.float32(np.divide(P12,P1*P2)))
		a[np.where(np.isfinite(a)==False)] = 0
		a[a < 0] = 0
		return a

	def PPMI(self):
		"""This function guides the PPMI calculation process
		"""
		dest_file = os.path.join(self.dest,
									 '_'.join([self.corpus,
											   'PPMI',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus,
											   'min_occ={0}'.format(self.min_count)]) + '.dat')
		if os.path.isfile(dest_file):
			self.PPMI_df = np.memmap(dest_file, dtype='float32', mode='r', shape=(len(self.ind), len(self.ind)))
			return
		n = np.sum(self.coll_df)
		#values for C2
		p2 = np.sum(self.coll_df, axis=1)/n
		self.PPMI_df = np.memmap(dest_file, dtype='float32', mode='w+', shape=(len(self.ind), len(self.ind)))
		for i, w in enumerate(self.ind):
			self.PPMI_df[i] = self.PMI_calc(i, p2, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.PPMI_df
				self.PPMI_df = np.memmap(dest_file, dtype='float32', mode='r+', shape=(len(self.ind), len(self.ind)))
		self.PPMI_df[np.where(np.isfinite(self.PPMI_df)==False)] = 0
		del self.PPMI_df
		self.PPMI_df = np.memmap(dest_file, dtype='float32', mode='r', shape=(len(self.ind), len(self.ind)))

	def CS(self, algorithm):
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
		dest_file = os.path.join(self.dest,
								 '_'.join([self.corpus,
										   algorithm,
										   'CS',
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   'SVD_exp={0}.dat'.format(str(self.svd))]))
		if algorithm == 'PPMI':
			self.stat_df = self.PPMI_df
		elif algorithm == 'LL':
			self.stat_df = self.LL_df
		self.CS_df = np.memmap(dest_file, dtype='float32', mode='w+', shape=(len(self.ind), len(self.ind)))
		self.CS_df[:] = 1-pairwise_distances(self.stat_df, metric='cosine', n_jobs=self.jobs)
		'''for i, w in enumerate(self.ind):
			self.CS_df[i] = 1-pairwise_distances(self.stat_df[i], self.stat_df, metric='cosine', n_jobs=jobs)
			if i % 5000 == 0:
				del self.CS_df
				self.CS_df = np.memmap(dest_file, dtype='float32', mode='r+', shape=(len(self.ind), len(self.ind)))
		'''
		del self.CS_df
		self.CS_df = np.memmap(dest_file, dtype='float32', mode='r', shape=(len(self.ind), len(self.ind)))
		'''
		try:
			self.df_to_hdf(self.CS_df, dest_file)
			del self.stat_df
		except AttributeError:
			print('Not saving CS file')
		'''
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
		if self.algo == 'both':
			print('Starting PPMI at {0}'.format(os.system('date')))
			self.PPMI()
			print('Starting LL at {0}'.format(os.system('date')))
			self.LL()
		elif self.algo == 'PPMI':
			self.PPMI()
		elif self.algo == 'LL':
			self.LL()
		del self.coll_df
		print('Finished with %s calculations for %s for '
				  'w=%s, lem=%s, weighted=%s at %s' %
				  (self.algo,
				   self.corpus,
				   str(self.w),
				   self.lems,
				   self.weighted,
				  datetime.datetime.now().time().isoformat()))

	def svd_calc(self, algorithm):
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
		if algorithm == 'PPMI':
			U, s, Vh = linalg.svd(self.PPMI_df)
			S = np.diag(s)
			self.PPMI_df = pd.DataFrame(np.dot(U, S**self.svd),
						 index=self.PPMI_df.index)
		elif algorithm == 'LL':
			U, s, Vh = linalg.svd(self.LL_df)
			S = np.diag(s)
			self.LL_df = pd.DataFrame(np.dot(U, S**self.svd),
						 index=self.LL_df.index)
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
		self.corpus = self.dir.split('/')[-1]

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
			if self.algo == 'both':
				self.svd_calc('PPMI')
				self.svd_calc('LL')
			elif self.algo == 'PPMI':
				self.svd_calc('PPMI')
			elif self.algo == 'LL':
				self.svd_calc('LL')
		if self.algo == 'both':
			self.CS('PPMI')
			self.CS('LL')
		elif self.algo == 'PPMI':
			self.CS('PPMI')
		elif self.algo == 'LL':
			self.CS('LL')

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
			self.weighted = False
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
		dest_file = '{0}/{1}_{2}_weighted={3}_lems={4}_perplexity.pickle'.format(orig, min_w, max_w, self.weighted, self.lems)
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
				c=int(sys.argv[8]),
				occ_dict=sys.argv[9],
				min_count=int(sys.argv[10])).runPipeline()
	if sys.argv[1] == "ParamTester":
		ParamTester(c=int(sys.argv[2])).RunTests(min_w=int(sys.argv[3]),
												 max_w=int(sys.argv[4]),
												 step=int(sys.argv[5]),
												 orig=sys.argv[6])
