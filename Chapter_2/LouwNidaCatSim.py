__author__ = 'matt'

import pandas as pd
import numpy as np
import sys
from pickle import dump
from tkinter.filedialog import askopenfilename

sys.setrecursionlimit(50000)

#word_cats = (('θεός', 12), ('ἔθνος', 11), ('λατρεύω', 53),
#             ('βασιλεύς', 37), ('ἡγέομαι', 36), ('γινώσκω', 28))

class CatSim:

	def __init__(self):
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = askopenfilename(title='Where is your Louw-Nida dictionary pickle?')
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []


	def LoadDF(self, w):
		raise NotImplementedError('LoadDF is not implemented on CatSim. '
								  'Instead, use a sub-class (CatSimWin or '
								  'CatSimSVD).')

	def SimCalc(self, w):
		self.scores[w] = {}
		mean, std = np.mean(self.df.values), np.std(self.df.values)
		print('%s average: %s, std: %s' % (w, mean, std))
		self.tot_words = 0
		self.words_no_93 = 0
		self.not_words = 0
		for cat in self.ln.keys():
			words = []
			for d in self.ln[cat]['words']:
				word = list(d.keys())[0]
				if word in self.df.index:
					words.append((word, d[word]))
					self.tot_words += 1
					self.good_words.append(word)
					if cat[0] != 93:
						self.words_no_93 += 1
				else:
					self.prob_words.append(word)
					self.not_words += 1
			self.scores[w][cat] = pd.DataFrame(index=words, columns=['Mean', 'STD +/-'])
			for word1 in words:
				vals = []
				for word2 in words:
					if word1[0] != word2[0]:
						vals.append(self.df.ix[word1[0], word2[0]])
				#scores[win][cat].ix[word1, 'Gloss'] = word1[1]
				#try:
				#	self.scores[w][cat].ix[word1, 'Mean'] = np.mean(vals)
				#	self.scores[w][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
				#except ValueError:
				self.scores[w][cat].drop_duplicates(inplace=True)
				self.scores[w][cat].ix[word1, 'Mean'] = np.mean(vals)
				self.scores[w][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std

	def AveCalc(self, w):
		total = 0
		total_no_93 = 0
		for cat in self.scores[w]:
			total += self.scores[w][cat].ix[:, 'STD +/-'].fillna(0).sum()
			if cat[0] != 93:
				total_no_93 += self.scores[w][cat].ix[:, 'STD +/-'].fillna(0).sum()
		self.averages[w] = total/self.tot_words
		self.ave_no_93[w] = total_no_93/self.words_no_93

	def WriteFiles(self):
		raise NotImplementedError('WriteFiles is not implemented on CatSim. '
								  'Instead, use a sub-class (CatSimWin or '
								  'CatSimSVD).')

	def WriteLines(self, save_file, w_size, svd_exp, lems):
		with open(save_file, mode='w', encoding='utf-8') as file:
			file.write('Scores for Window Size {0}, SVD Exponent {1}\n'.format(w_size, svd_exp))
			file.write('Category,Word,Gloss,# of Occurrences,Mean CS with Category,'
					   'Standard Deviations +/- Average\n')
			if self.rng_type == 'win':
				key = w_size
			else:
				key = svd_exp
			for cat in sorted(self.scores[key].keys()):
				for w in self.scores[key][cat].index:
					try:
						file.write(
							'{0}.{1}-{2} {3},{4},{5},{6},{7},{8}\n'.format
							(
								cat[0],
								cat[1],
								cat[2],
								self.ln[cat]['gloss'].replace(',', ' '),
								w[0],
								w[1].replace(',', ' '),
								lems[w[0]]['count'],
								self.scores[key][cat].ix[w, 'Mean'][0],
								self.scores[key][cat].ix[w, 'STD +/-'][0]
							)
						)
					except IndexError:
						file.write(
							'{0}.{1}-{2} {3},{4},{5},{6},{7},{8}\n'.format
							(
								cat[0],
								cat[1],
								cat[2],
								self.ln[cat]['gloss'].replace(',', ' '),
								w[0],
								w[1].replace(',', ' '),
								lems[w[0]]['count'],
								self.scores[key][cat].ix[w, 'Mean'],
								self.scores[key][cat].ix[w, 'STD +/-']
							)
						)

	def CatSimPipe(self):
		for w in self.rng:
			self.LoadDF(w)
			self.SimCalc(w)
			self.AveCalc(w)
		self.WriteFiles()
		prob_words = list(set(self.prob_words))
		good_words = list(set(self.good_words))
		print('prob_words', len(prob_words), prob_words[:10])
		print('good_words', len(good_words), good_words[:10])
		print(self.averages, self.ave_no_93)

class CatSimWin(CatSim):

	def __init__(self):
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = askopenfilename(title='Where is your Louw-Nida dictionary pickle?')
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng_type = 'win'
		self.rng = (20, 60, 100, 200, 300, 350, 400, 450, 500)

	def LoadDF(self, w):
		file = 'Data/{0}/PPMI_CS_{0}_SBL_GNT_SVD_exp={1}.pickle'.format(str(w), 'None')
		try:
			self.df = pd.read_pickle(file)
		except FileNotFoundError:
			file = askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format(str(w), 'None'))
			self.df = pd.read_pickle(file)

	def WriteFiles(self):
		with open('Data/Chapter_2/LN_Word_Cat_Scores.pickle', mode='wb') as file:
			dump(self.scores, file)
		lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
		for w_size in self.scores.keys():
			save_file = 'Data/Chapter_2/LN_Window={0}_Word_Cat_Scores_SVD_exp={1}.csv'.format(str(w_size), 'None')
			self.WriteLines(save_file, w_size, 'None', lems)
		with open('Data/Chapter_2/LN_Window_Averages.pickle', mode='wb') as file:
			dump(self.averages, file)
		with open('Data/Chapter_2/LN_Window_Averages.csv',
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window\n')
			file.write('Window Size,Average,+/- Standard Deviations\n')
			for w_size in sorted(self.averages.keys()):
				file.write('{0},{1}\n'.format(w_size, self.averages[w_size]))
		with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.pickle', mode='wb') as file:
			dump(self.ave_no_93, file)
		with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.csv',
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window excluding LN Category 93 (Names)\n')
			file.write('Window Size,Average +/- Standard Deviations\n')
			for w_size in sorted(self.ave_no_93.keys()):
				file.write('{0},{1}\n'.format(w_size, self.ave_no_93[w_size]))

class CatSimSVD(CatSim):

	def __init__(self):
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = askopenfilename(title='Where is your Louw-Nida dictionary pickle?')
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng_type = 'svd'
		self.rng = (.1, .25, .4, .55, .7, .85, 1, 1.15, 1.3, 1.45, 1.6)

	def LoadDF(self, w):
		file = 'Data/{0}/PPMI_CS_{0}_SBL_GNT_SVD_exp={1}.pickle'.format('350', w)
		try:
			self.df = pd.read_pickle(file)
		except FileNotFoundError:
			file = askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format('350', w))
			self.df = pd.read_pickle(file)

	def WriteFiles(self):
		with open('Data/Chapter_2/LN_Word_Cat_Scores_SVD.pickle', mode='wb') as file:
			dump(self.scores, file)
		lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
		for w_size in self.scores.keys():
			save_file = 'Data/Chapter_2/LN_Window={0}_Word_Cat_Scores_SVD_exp={1}.csv'.format('350', str(w_size))
			self.WriteLines(save_file, '350', w_size, lems)
		with open('Data/Chapter_2/LN_Window_Averages_SVD.pickle', mode='wb') as file:
			dump(self.averages, file)
		with open('Data/Chapter_2/LN_Window_Averages_SVD.csv',
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per SVD Exponent\n')
			file.write('SVD Exponent,Average,+/- Standard Deviations\n')
			for w_size in sorted(self.averages.keys()):
				file.write('{0},{1}\n'.format(w_size, self.averages[w_size]))
		with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.pickle', mode='wb') as file:
			dump(self.ave_no_93, file)
		with open('Data/Chapter_2/LN_Window_Averages_no_93_SVD.csv',
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window excluding LN Category 93 (Names)\n')
			file.write('Window Size,Average +/- Standard Deviations\n')
			for w_size in sorted(self.ave_no_93.keys()):
				file.write('{0},{1}\n'.format(w_size, self.ave_no_93[w_size]))

class WordCatFinder(CatSim):

	def __init__(self, words):
		if type(words) != list:
			raise TypeError('"words" must be a list')
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = askopenfilename(title='Where is your Louw-Nida dictionary pickle?')
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng = words

	def LoadDF(self):
		file = 'Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle'
		try:
			self.df = pd.read_pickle(file)
		except FileNotFoundError:
			file = askopenfilename(title='Where is your pickle file for window = 350, svd exponent = 1.45')
			self.df = pd.read_pickle(file)

	def SimCalc(self, w):
		self.scores[w] = {}
		mean, std = np.mean(self.df.values), np.std(self.df.values)
		print(w)
		self.scores[w] = pd.DataFrame(index=list(self.ln.keys()),
										  columns=['Mean', 'STD +/-'])
		for cat in self.ln.keys():
			vals = []
			cat_words = []
			for d in self.ln[cat]['words']:
				word = list(d.keys())[0]
				if word in self.df.index:
					cat_words.append((word, d[word]))
					self.good_words.append(word)
				else:
					self.prob_words.append(word)
			for word1 in cat_words:
				if word1[0] != w:
					vals.append(self.df.ix[word1[0], w])
			self.scores[w].ix[cat, 'Mean'] = np.mean(vals)
			self.scores[w].ix[cat, 'STD +/-'] = (np.mean(vals)-mean)/std

	def WriteFiles(self):
		with open('Data/Chapter_2/LN_Word_Cat_Finder_SVD.pickle', mode='wb') as file:
			dump(self.scores, file)
		#lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
		save_file = 'Data/Chapter_2/LN_Word_Cat_Finder_SVD.csv'
		self.WriteLines(save_file)

	def WriteLines(self, save_file):
		print('Writing Lines')
		with open(save_file, mode='w', encoding='utf-8') as file:
			file.write('Scores for Window Size 350; SVD Exponent 1.45\n')
			file.write('Word,Category,Mean CS with Category,'
					   'Standard Deviations +/- Average\n')
			for word in self.scores.keys():
				for cat in sorted(self.scores[word].index):
					try:
						file.write(
							'{0},{1}.{2}-{3} {4},{5},{6}\n'.format
							(
								word,
								cat[0],
								cat[1],
								cat[2],
								self.ln[cat]['gloss'].replace(',', ' '),
								self.scores[word].ix[cat, 'Mean'][0],
								self.scores[word].ix[cat, 'STD +/-'][0]
							)
						)
					except IndexError:
						file.write(
							'{0},{1}.{2}-{3} {4},{5},{6}\n'.format
							(
								word,
								cat[0],
								cat[1],
								cat[2],
								self.ln[cat]['gloss'].replace(',', ' '),
								self.scores[word].ix[cat, 'Mean'],
								self.scores[word].ix[cat, 'STD +/-']
							)
						)

	def CatSimPipe(self):
		self.LoadDF()
		for w in self.rng:
			self.SimCalc(w)
		self.WriteFiles()