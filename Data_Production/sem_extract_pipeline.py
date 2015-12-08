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
from proj.tasks import counter, svd_calc
from sklearn.cross_validation import KFold
from pickle import dump
from copy import deepcopy



class SemPipeline:

	def __init__(self, win_size=350, lemmata=True, weighted=True, algo='PPMI', sim_algo='cosine', svd=1, files=None, c=8, occ_dict=None, min_count=1, jobs=1, stops=True):
		"""
		"""
		self.w = win_size
		self.lems = lemmata
		self.weighted = weighted
		self.algo = algo
		if sim_algo in ['cityblock', 'cosine', 'euclidean', 'l1', 'l2', 'manhattan']:
			self.sim_algo = sim_algo
		else:
			print("The only accepted values for 'sim_algo' are 'cityblock', 'cosine', 'euclidean', 'l1', 'l2', or 'manhattan'")
			print("Setting 'sim_algo' to 'cosine'")
			self.sim_algo = 'cosine'
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
		if stops == False:
			self.stops = ['μή', 'ἑαυτοῦ', 'ἄν', 'ἀλλ’', 'ἀλλά', 'ἄλλος', 'ἀπό',
						  'ἄρα', 'αὐτός', 'δ’', 'δέ', 'δή', 'διά', 'δαί',
						  'δαίς', 'ἔτι', 'ἐγώ', 'ἐκ', 'ἐμός', 'ἐν', 'ἐπί',
						  'εἰ', 'εἰμί', 'εἴμι', 'εἰς', 'γάρ', 'γε', 'γα^', 'ἡ',
						  'ἤ', 'καί', 'κατά', 'μέν', 'μετά', 'μή', 'ὁ', 'ὅδε',
						  'ὅς', 'ὅστις', 'ὅτι', 'οὕτως', 'οὗτος', 'οὔτε', 'οὖν',
						  'οὐδείς', 'οἱ', 'οὐ', 'οὐδέ', 'οὐκ', 'περί', 'πρός',
						  'σύ', 'σύν', 'τά', 'τε', 'τήν', 'τῆς', 'τῇ', 'τι',
						  'τί', 'τις', 'τίς', 'τό', 'τοί', 'τοιοῦτος', 'τόν',
						  'τούς', 'τοῦ', 'τῶν', 'τῷ', 'ὑμός', 'ὑπέρ', 'ὑπό',
						  'ὡς', 'ὦ', 'ὥστε', 'ἐάν', 'παρά', 'σός']
		else:
			self.stops = []


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
		words = []
		if self.lems:
			pattern = re.compile(r'.+?lem="([^"]*).*')
		else:
			pattern = re.compile(r'.+?>([^<]*).*')
		for line in self.t:
			word = re.sub(pattern, r'\1', line).lower()
			if word != '' and word not in self.stops:
				words.append(word)
		return words


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
										   self.corpus,
										   'min_occ={0}'.format(self.min_count),
										   'no_stops={0}'.format(bool(self.stops)),
										   'weighted={}'.format(self.weighted)]) + '.dat')
		if os.path.isfile(cooc_dest):
			self.ind = pd.read_pickle('{0}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)))
			#the following line deals with the case when the cooc matrix is not square
			try:
				occs = pd.read_pickle('{0}/{1}_ColumnList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)))
				self.cols = len(occs)
			except:
				self.cols = len(self.ind)
			self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r', shape=(len(self.ind), self.cols))
			return
		counts = Counter()
		if self.occ_dict:
			occs = pd.read_pickle(self.occ_dict)
			min_lems = set([w for w in occs if occs[w] < self.min_count])
			#the following line deals with the case when the cooc matrix is not square
			#self.col_ind = list(occs.keys())
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
		try:
			assert(self.col_ind)
		except AttributeError:
			self.col_ind = self.ind
		self.cols = len(self.col_ind)
		with open('{0}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)), mode='wb') as f:
			dump(self.ind, f)
		with open('{0}/{1}_ColumnList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)), mode='wb') as f:
			dump(self.col_ind, f)
		print('Now writing cooccurrence file at {0}'.format(datetime.datetime.now().time().isoformat()))
		self.coll_df = np.memmap(cooc_dest, dtype='float', mode='w+', shape=(len(self.ind), len(self.col_ind)))
		for i, w in enumerate(self.ind):
			s = pd.Series(counts[w], index=self.col_ind, dtype=np.float64).fillna(0)
			self.coll_df[i] = s.values
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.coll_df
				self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r+', shape=(len(self.ind), len(self.col_ind)))
		del self.coll_df
		self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r', shape=(len(self.ind), len(self.col_ind)))
		'''
		for (ind, key), (ind2, key2) in combinations(enumerate(self.ind), 2):
			count += 1
			self.coll_df[ind, ind2] = counts[key][key2]
			self.coll_df[ind2, ind] = counts[key2][key]
			if count % 1000 == 0:
				self.coll_df.flush()
		'''
		#self.coll_df = pd.DataFrame(counts, dtype=np.float).fillna(0)
		#try:
		#	self.df_to_hdf(self.coll_df, cooc_dest)
		#except AttributeError:
		#	print('Cooccurrence calculation finished')

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
									 '_'.join(['LL',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus,
											   'min_occ={0}'.format(self.min_count),
											   'no_stops={0}'.format(bool(self.stops)),
											   'weighted={}'.format(self.weighted)]) + '.dat')
		if os.path.isfile(dest_file):
			self.LL_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), self.cols))
			return
		n = np.sum(self.coll_df)
		c2 = np.sum(self.coll_df, axis=0)
		p = c2/n
		self.LL_df = np.memmap(dest_file, dtype='float', mode='w+', shape=(len(self.ind), self.cols))
		for i, w in enumerate(self.ind):
			self.LL_df[i] = self.log_like(i, c2, p, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.LL_df
				self.LL_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(len(self.ind), self.cols))
		self.LL_df[np.where(np.isfinite(self.LL_df)==False)] = 0
		del self.LL_df
		self.LL_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), self.cols))

		'''
		self.stat_df = pd.DataFrame(0., index=self.coll_df.index,
							 columns=self.coll_df.index, dtype=np.float)
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
		a = np.log2(np.divide(P12,P1*P2))
		a[np.where(np.isfinite(a)==False)] = 0
		a[a < 0] = 0
		return a

	def PPMI(self):
		"""This function guides the PPMI calculation process
		"""
		dest_file = os.path.join(self.dest,
									 '_'.join(['PPMI',
											   str(self.w),
											   'lems={0}'.format(self.lems),
											   self.corpus,
											   'min_occ={0}'.format(self.min_count),
											   'no_stops={0}'.format(bool(self.stops)),
											   'weighted={}'.format(self.weighted)]) + '.dat')
		if os.path.isfile(dest_file):
			self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), self.cols))
			return
		n = np.sum(self.coll_df)
		#values for C2
		p2 = np.sum(self.coll_df, axis=0)/n
		self.PPMI_df = np.memmap(dest_file, dtype='float', mode='w+', shape=(len(self.ind), self.cols))
		for i, w in enumerate(self.ind):
			self.PPMI_df[i] = self.PMI_calc(i, p2, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del self.PPMI_df
				self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(len(self.ind), self.cols))
		self.PPMI_df[np.where(np.isfinite(self.PPMI_df)==False)] = 0
		del self.PPMI_df
		self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), self.cols))

	def CS(self, algorithm, e):
		"""This function calls the pairwise distance function from sklearn
		on every log-likelihood DataFrame in a certain directory and returns
		the similarity score (i.e., 1-cosine distance) for every word, saving
		the results then to a different directory.
		"""
		print('Starting {} calculations for {} for '
				  'w={}, lem={}, weighted={} svd={} at {}'.format(self.sim_algo,
																  self.corpus,
																  str(self.w),
																  self.lems,
																  self.weighted,
																  e,
																  datetime.datetime.now().time().isoformat()))
		dest_file = os.path.join(self.dest,
								 '_'.join([algorithm,
										   self.sim_algo,
										   str(self.w),
										   'lems={0}'.format(self.lems),
										   self.corpus,
										   'min_occ={0}'.format(self.min_count),
										   'SVD_exp={0}'.format(str(e)),
										   'no_stops={0}'.format(bool(self.stops)),
										   'weighted={}.dat'.format(self.weighted)]))
		if os.path.isfile(dest_file):
			return
		if e == 1:
			if algorithm == 'PPMI':
				self.stat_df = self.PPMI_df
			elif algorithm == 'LL':
				self.stat_df = self.LL_df
		else:
			orig = os.path.join(self.dest,
										'_'.join([algorithm,
												  'SVD',
												  str(self.w),
												  'lems={0}'.format(self.lems),
												  self.corpus,
												  'min_occ={0}'.format(self.min_count),
												  'SVD_exp={0}'.format(str(e)),
												  'no_stops={0}'.format(bool(self.stops)),
												  'weighted={}.dat'.format(self.weighted)]))
			self.stat_df = np.memmap(orig, dtype='float', mode='r', shape=(len(self.ind), self.cols))
		self.CS_df = np.memmap(dest_file, dtype='float', mode='w+', shape=(len(self.ind), len(self.ind)))
		if self.sim_algo == 'cosine':
			self.CS_df[:] = 1-pairwise_distances(self.stat_df, metric=self.sim_algo, n_jobs=self.jobs)
		else:
			self.CS_df[:] = pairwise_distances(self.stat_df, metric=self.sim_algo, n_jobs=self.jobs)
		'''for i, w in enumerate(self.ind):
			self.CS_df[i] = 1-pairwise_distances(self.stat_df[i], self.stat_df, metric='cosine', n_jobs=jobs)
			if i % 5000 == 0:
				del self.CS_df
				self.CS_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(len(self.ind), len(self.ind)))
		'''
		del self.CS_df
		self.CS_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))
		'''
		try:
			self.df_to_hdf(self.CS_df, dest_file)
			del self.stat_df
		except AttributeError:
			print('Not saving CS file')
		'''
		print('Finished with {} calculations for {} for '
				  'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
														   self.corpus,
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
		#dest_file = os.path.join(self.dest,
		#						 '_'.join([algorithm,
		#								   'SVD',
		#								   str(self.w),
		#								   'lems={0}'.format(self.lems),
		#								   self.corpus,
		#								   'min_occ={0}'.format(self.min_count),
		#								   'SVD_exp={0}.dat'.format(str(self.svd))]))
		#if os.path.isfile(dest_file):
			#self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r', shape=(len(self.ind), self.cols))
			#return
		#svd_df = np.memmap(dest_file, dtype='float', mode='w+', shape=(len(self.ind), self.cols))
		if algorithm == 'PPMI':
			orig = os.path.join(self.dest,
								'_'.join(['PPMI',
										  str(self.w),
										  'lems={0}'.format(self.lems),
										  self.corpus,
										  'min_occ={0}'.format(self.min_count),
										  'no_stops={0}'.format(bool(self.stops)),
										   'weighted={}'.format(self.weighted)]) + '.dat')
			pause = group(svd_calc.s(orig, os.path.join(self.dest,
														'_'.join([algorithm,
																  'SVD',
																  str(self.w),
																  'lems={0}'.format(self.lems),
																  self.corpus,
																  'min_occ={0}'.format(self.min_count),
																  'SVD_exp={0}'.format(str(e)),
																  'no_stops={0}'.format(bool(self.stops)),
																  'weighted={}.dat'.format(self.weighted)])),
									 e, (len(self.ind), self.cols)) for e in self.svd)().get()
			#U, s, Vh = linalg.svd(self.PPMI_df, check_finite=False)
			#S = np.diag(s)
			#svd_df[:] = np.dot(U, np.power(S, self.svd))
			#self.PPMI_df = svd_df
		elif algorithm == 'LL':
			orig = os.path.join(self.dest,
								'_'.join(['LL',
										  str(self.w),
										  'lems={0}'.format(self.lems),
										  self.corpus,
										  'min_occ={0}'.format(self.min_count),
										  'no_stops={0}'.format(bool(self.stops)),
										   'weighted={}'.format(self.weighted)]) + '.dat')
			pause = group(svd_calc.s(orig, os.path.join(self.dest,
														'_'.join([algorithm,
																  'SVD',
																  str(self.w),
																  'lems={0}'.format(self.lems),
																  self.corpus,
																  'min_occ={0}'.format(self.min_count),
																  'SVD_exp={0}'.format(str(e)),
																  'no_stops={0}'.format(bool(self.stops)),
																  'weighted={}.dat'.format(self.weighted)])),
									 e, (len(self.ind), self.cols)) for e in self.svd)().get()
			#U, s, Vh = linalg.svd(self.LL_df, check_finite=False)
			#S = np.diag(s)
			#svd_df[:] = np.dot(U, np.power(S, self.svd))
			#self.PPMI_df = svd_df
		print(pause)
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
		if type(self.svd) != list:
			self.svd = [float(self.svd)]
		if self.svd != [1]:
			if self.algo == 'both':
				self.svd_calc('PPMI')
				self.svd_calc('LL')
			elif self.algo == 'PPMI':
				self.svd_calc('PPMI')
			elif self.algo == 'LL':
				self.svd_calc('LL')
		for exp in self.svd:
			if self.algo == 'both':
				self.CS('PPMI', exp)
				self.CS('LL', exp)
			elif self.algo == 'PPMI':
				self.CS('PPMI', exp)
			elif self.algo == 'LL':
				self.CS('LL', exp)

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

	def __init__(self, c=8, jobs=1, min_count=1, orig=None):
		"""
		"""
		self.c = c
		self.occ_dict = None
		self.stops = []
		self.jobs = jobs
		self.min_count = min_count
		self.orig = orig

	def word_extract(self):
		'''
		Extracts all of the words/lemmata from the lines extracted from
		the XML file
		'''
		words = []
		if self.lems:
			pattern = re.compile(r'.+?lem="([^"]*).*')
		else:
			pattern = re.compile(r'.+?>([^<]*).*')
		for line in self.t:
			word = re.sub(pattern, r'\1', line).lower().replace('/', '')
			if word != '' and word not in self.stops:
				words.append(word)
		return words

	def cooc_counter(self, files):
		'''
		This function takes a token list, a windows size (default
		is 4 left and 4 right), and a destination filename, runs through the
		token list, reading every word to the window left and window right of
		the target word, and then keeps track of these co-occurrences in a
		cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
		this dictionary and then pickles this DataFrame to dest
		'''
		#self.coll_df = pd.DataFrame()
		counts = Counter()
		if self.occ_dict:
			occs = pd.read_pickle(self.occ_dict)
			min_lems = set([w for w in occs if occs[w] < self.min_count])
			#the following line deals with the case when the cooc matrix is not square
			#self.col_ind = list(occs.keys())
			del occs
		else:
			min_lems = set()
		for file in files:
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
		col_ind = list(counts.keys())
		cols = len(col_ind)
		return pd.SparseDataFrame.from_dict(counts, orient='index', dtype=np.float64).fillna(0)

	def log_like(self, row, C2, P, N):
		'''
		values for c12
		this is the row in the coll_df that I am looking at
		'''
		C12 = self.coll_df[row].to_dense()
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
		LL2 = self.log_space_L(C2-C12, N-C1, P)


		'''
		The following finds all inf and -inf values in LL2 by
		moving calculations into log space.
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

		return -2 * (LL1 + LL2 - LL3 - LL4)

	def LL(self):
		"""This function guides the log-likelihood calculation process
		"""
		n = np.sum(self.coll_df.values)
		c2 = np.sum(self.coll_df, axis=0)
		p = c2/n
		LL_df = np.memmap('{}/LL_memmap.dat'.format(self.orig), dtype='float', mode='w+', shape=(len(self.ind), len(self.ind)))
		for i, w in enumerate(self.ind):
			LL_df[i] = self.log_like(w, c2, p, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del LL_df
				LL_df = np.memmap('{}/LL_memmap.dat'.format(self.orig), dtype='float', mode='r+', shape=(len(self.ind), len(self.ind)))
		LL_df[np.where(np.isfinite(LL_df)==False)] = 0
		del LL_df
		LL_df = np.memmap('{}/LL_memmap.dat'.format(self.orig), dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))
		return LL_df

	def PMI_calc(self, row, P2, N):
		'''
		values for c12
		this is the row in the coll_df that I am looking at
		'''
		C12 = self.coll_df[row].to_dense()
		#value for C1 will be a scalar value used for all calculations on
		#that row
		C1 = np.sum(C12)
		P1 = C1/N
		P12 = C12/N
		a = np.log2(np.divide(P12,P1*P2))
		a[a < 0] = 0
		return a

	def PPMI(self):
		"""This function guides the PPMI calculation process
		"""
		n = np.sum(self.coll_df.values)
		p2 = np.sum(self.coll_df, axis=0)/n
		PPMI_df = np.memmap('{}/PPMI_memmap.dat'.format(self.orig), dtype='float', mode='w+', shape=(len(self.ind), len(self.ind)))
		for i, w in enumerate(self.ind):
			PPMI_df[i] = self.PMI_calc(w, p2, n)
			if i % 5000 == 0:
				print('{0}% done'.format((i/len(self.ind)*100)))
				del PPMI_df
				PPMI_df = np.memmap('{}/PPMI_memmap.dat'.format(self.orig), dtype='float', mode='r+', shape=(len(self.ind), len(self.ind)))
		PPMI_df[np.where(np.isfinite(PPMI_df)==False)] = 0
		del PPMI_df
		PPMI_df = np.memmap('{}/PPMI_memmap.dat'.format(self.orig), dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))
		return PPMI_df

	def scaler(self, df):
		"""Scales the values of the given DataFrame to a range between
		0 and 1

		:param df:
		"""
		from sklearn.preprocessing import StandardScaler
		df1 = deepcopy(df)
		scaled = pd.DataFrame(StandardScaler().fit_transform(df1),
							  index = df.index,
							  columns = df.columns)
		return (scaled + 1)

	def RunTests(self, min_w, max_w, step, lem_file=None, w_tests=(True, False), l_tests=(True, False)):

		from Chapter_2.LouwNidaCatSim import CatSimWin
		self.param_dict = {}
		files = glob('{0}/*.txt'.format(self.orig))
		for self.w in range(min_w, max_w+1, step):
			for self.weighted in w_tests:
				for self.lems in l_tests:
					prob_list = []
					pmi_list = []
					counter = 1
					print('weighted %s, lemmata %s, w=%s at %s' %
						  (self.weighted,
						   self.lems,
						   self.w,
						   datetime.datetime.now().time().isoformat()))

					self.coll_df = self.cooc_counter(files)
					self.ind = list(self.coll_df.index)
					LL_df = self.LL()
					self.coll_df.to_pickle('{}/coll_df.pickle'.format(self.orig))
					del self.coll_df
					pipe = CatSimWin('LL', self.w, lems=self.lems, CS_dir=self.orig, dest_dir='{}/Win_size_tests/LN'.format(self.orig), sim_algo='cosine', corpus=(self.orig.split('/')[-1], 1, 1.0, self.weighted), lem_file=lem_file)
					pipe.df = 1-pairwise_distances(LL_df, metric='cosine', n_jobs=self.jobs)
					del LL_df
					pipe.ind = self.ind
					pipe.SimCalc(self.w)
					pipe.AveCalc(self.w)
					pipe.WriteFiles()
					self.param_dict['LL_window={}_lems={}_weighted={}'.format(self.w, self.lems, self.weighted)] = pipe.ave_no_93[self.w]
					del pipe
					self.coll_df = pd.read_pickle('{}/coll_df.pickle'.format(self.orig))
					PPMI_df = self.PPMI()
					del self.coll_df
					pipe = CatSimWin('PPMI', self.w, lems=self.lems, CS_dir=self.orig, dest_dir='{}/Win_size_tests/LN'.format(self.orig), sim_algo='cosine', corpus=(self.orig.split('/')[-1], 1, 1.0, self.weighted), lem_file=lem_file)
					pipe.df = 1-pairwise_distances(PPMI_df, metric='cosine', n_jobs=self.jobs)
					del PPMI_df
					pipe.ind = self.ind
					pipe.SimCalc(self.w)
					pipe.AveCalc(self.w)
					pipe.WriteFiles()
					self.param_dict['PPMI_window={}_lems={}_weighted={}'.format(self.w, self.lems, self.weighted)] = pipe.ave_no_93[self.w]
					del pipe
			print(self.param_dict)
		dest_file = '{0}/Win_size_tests/{5}_{1}_{2}_weighted={3}_lems={4}.pickle'.format(self.orig, os.path.basename(self.orig), min_w, max_w, w_tests, l_tests)
		with open(dest_file, mode='wb') as f:
			dump(self.param_dict, f)
		with open(dest_file.replace('.pickle', '.csv'), mode='w') as f:
			f.write('Test Details\tMean Category Score\tCategory Z-Score')
			for k in sorted(self.param_dict.keys(), key=lambda x: int(x.split('_')[1].split('=')[1])):
				f.write('\n{}\t{}\t{}'.format(k, self.param_dict[k][0], self.param_dict[k][1]))


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
