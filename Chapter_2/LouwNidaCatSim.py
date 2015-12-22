__author__ = 'matt'

import pandas as pd
import numpy as np
import sys
from pickle import dump
try:
	from Data_Production.TK_files import tk_control
except ImportError:
	print('Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')

sys.setrecursionlimit(50000)

#word_cats = (('θεός', 12), ('ἔθνος', 11), ('λατρεύω', 53),
#             ('βασιλεύς', 37), ('ἡγέομαι', 36), ('γινώσκω', 28))

class CatSim:

	def __init__(self):
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = tk_control("askopenfilename(title='Where is your Louw-Nida dictionary pickle?')")
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.prob_word_replace = {'περιΐστημι': 'περιΐστημι',
									'προΐστημι': 'προΐστημι',
									'παρατεινω': 'παρατείνω',
									'μήπως': '',
									'ταβέρνη': 'Ταβέρνη',
									'ἀναμάρτητος': '',
									'προσεγγίζω': '',
									'ηλι': 'ἠλί',
									'δανειστής': 'δανιστής',
									'κατακύπτω':  '',
									'πρωΐ': 'πρωΐ',
									'τυρβάζω': '',
									'Θυάτιρα': 'Θυάτειρα',
									'τετράπουν': 'τετράπους',
									'ἰουδαΐζω': 'ἰουδαΐζω',
									'Τρωγύλλιον': '',
									'σεβαστός': 'Σεβαστός',
									'σωτήριον': 'σωτήριος',
									'κακοπάθεια': 'κακοπαθία',
									'προσανατίθεμαι': 'προσανατίθημι',
									'Χερούβ': 'Χεροῦβ',
									'πρωΐα': 'πρωΐα',
									'Σαλίμ': 'Σαλείμ',
									'νόσημα': '',
									'διΐστημι': 'διΐστημι',
									'Νικολαΐτης': 'Νικολαΐτης',
									'αὐτόφωρος': '',
									'ὅμιλος': '',
									'μαρανα': [],
									'Ματθάτ': 'Ματθάν',
									'ὀρεινή': 'ὀρεινός',
									'δευτερόπρωτος': '',
									'ἔξεστι': 'ἔξεστι(ν)',
									'τομός': 'τομώτερος',
									'πειραω': 'πειράω',
									'ῥυπαίνομαι': 'ῥυπαρεύω',
									'Λεββαιος': '',
									'ελωι': 'ἐλωΐ',
									'πραΰς': 'πραΰς',
									'ὑπερβαίνω': '',
									'ὅποτε': 'ὁπότε',
									'ἐνεός': 'ἐνέος',
									'τεσσαρακονταετής': 'τεσσερακονταετής',
									'ἀγαθοποιΐα': 'ἀγαθοποιΐα',
									'Σάπφειρα': 'Σάπφιρα',
									'σαβαχθανι': 'σαβαχθάνι',
									'στοιχεῖα': 'στοιχεῖον',
									'συζήτησις': '',
									'ἐκτίθεμαι': 'ἐκτίθημι',
									'Κλῆμης': 'Κλήμης',
									'τάραχή': 'τάραχος',
									'Πάρθοι': 'Πάρθος',
									'λεμα': 'λεμά',
									'Λωΐς': 'Λωΐς',
									'Βηθζαθά': 'Βηθεσδά',
									'πίμπραμαι': 'πίμπρημι',
									'Σεμεΐν': 'Σεμεΐν',
									'Νεάπολις': '',
									'Νύμφας': 'Νύμφα',
									'πλείων': 'πολύς',
									'Πτολεμαΐς': 'Πτολεμαΐς',
									'Βηθαβαρα': '',
									'Ῥωμαικος': '',
									'ἐκλανθάνομαι': 'ἐκλανθάνω',
									'Βενιαμείν': 'Βενιαμίν',
									'Ἰουνιᾶς': 'Ἰουνία',
									'πραΰτης': 'πραΰτης',
									'ῥεδή': 'ῥέδη',
									'καταβιβαζω': 'καταβαίνω',
									'σπόριμα': 'σπόριμος',
									'Ἀχαΐα': 'Ἀχαΐα',
									'εὐποιΐα': 'εὐποιΐα',
									'ἀνάτεμα': 'ἀνάθεμα',
									'ὀσφῦς': 'ὀσφύς',
									'κηριον': '',
									'Ναΐν': 'Ναΐν',
									'θα': 'θά',
									'δήποτε': '',
									'θρῆνος': '',
									'Ἠσαΐας': 'Ἠσαΐας',
									'καταγράφω': '',
									'Καλοι Λιμένης': '',
									'πραϋπάθεια': 'πραϋπαθία',
									'τεσσαράκοντα': 'τεσσεράκοντα',
									'μελισσιος': '',
									'Γεργεσηνός': 'Γερασηνός',
									'Ἑβραικός': '',
									'ἅλς': '',
									'Φάρες': 'Φαρές',
									'λόγια': 'λογεία',
									'ἀΐδιος': 'ἀΐδιος',
									'ἀγραύλεω': 'ἀγραυλέω',
									'νεομηνία': 'νουμηνία',
									'Ἑβραΐς': 'Ἑβραΐς',
									'Ἀβραάμ': 'Ἀβραάμ'.lower()}


	def LoadDF(self, w):
		raise NotImplementedError('LoadDF is not implemented on CatSim. '
								  'Instead, use a sub-class (CatSimWin or '
								  'CatSimSVD).')

	def SimCalc(self, w):
		self.scores[w] = {}
		try:
			mean, std = np.mean(self.df.values), np.std(self.df.values)
		except AttributeError:
			mean, std = np.mean(self.df), np.std(self.df)
		print('%s average: %s, std: %s' % (w, mean, std))
		self.tot_words = 0
		self.words_no_93 = 0
		self.not_words = 0
		for cat in self.ln.keys():
			words = []
			for d in self.ln[cat]['words']:
				word = list(d.keys())[0]
				if word.lower() in self.ind:
					words.append((word.lower(), str(d[word])))
					self.tot_words += 1
					self.good_words.append(word)
					if cat[0] != 93:
						self.words_no_93 += 1
				else:
					try:
						new_word = self.prob_word_replace[word]
						if new_word != '':
							words.append((new_word.lower(), str(d[word])))
						self.tot_words += 1
						self.good_words.append(w)
						if cat[0] != 93:
							self.words_no_93 += 1
						self.prob_words.append(word)
						self.not_words += 1
					except KeyError:
						continue
			try:
				words = list(set(words))
			except TypeError:
				print(words)
				print(type(words))
			self.scores[w][cat] = pd.DataFrame(index=words, columns=['Mean', 'STD +/-'])
			#print(self.scores[w][cat].index)
			for word1 in words:
				vals = []
				for word2 in words:
					if word1[0] != word2[0]:
						try:
							vals.append(self.df[self.ind.index(word1[0])][self.ind.index(word2[0])])
						except ValueError:
							continue
				#scores[win][cat].ix[word1, 'Gloss'] = word1[1]
				#try:
				#	self.scores[w][cat].ix[word1, 'Mean'] = np.mean(vals)
				#	self.scores[w][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
				#except ValueError:
				#self.scores[w][cat].drop_duplicates(inplace=True)
				try:
					self.scores[w][cat].ix[word1, 'Mean'] = np.mean(vals)
				except KeyError:
					print(word1)
					print(words)
					print(self.scores[w][cat].index)
					print(self.scores[w][cat])
				self.scores[w][cat].ix[word1, 'STD +/-'] = (np.mean(vals)-mean)/std
		print('Total words: {0}'.format(self.words_no_93))

	def AveCalc(self, w):
		total_std = 0
		total_mean = 0
		total_no_93_std = 0
		total_no_93_mean = 0
		for cat in self.scores[w]:
			total_mean +=self.scores[w][cat].ix[:, 'Mean'].fillna(0).sum()
			total_std += self.scores[w][cat].ix[:, 'STD +/-'].fillna(0).sum()
			if cat[0] != 93:
				total_no_93_mean += self.scores[w][cat].ix[:, 'Mean'].fillna(0).sum()
				total_no_93_std += self.scores[w][cat].ix[:, 'STD +/-'].fillna(0).sum()
		self.averages[w] = (total_mean/self.tot_words, total_std/self.tot_words)
		self.ave_no_93[w] = (total_no_93_mean/self.words_no_93, total_no_93_std/self.words_no_93)

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
						cnt = lems[w[0]]
					except KeyError:
						cnt = '?'
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
								cnt,
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
								cnt,
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

	def __init__(self, algo, rng, lems=False, CS_dir=None, dest_dir=None, sim_algo=None, corpus=('SBL_GNT_books', 1, 1.0, True), lem_file = None):
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = tk_control("askopenfilename(title='Where is your Louw-Nida dictionary pickle?')")
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng_type = 'win'
		self.rng = rng
		self.algo = algo
		self.CS_dir = CS_dir
		self.dest_dir = dest_dir
		self.corpus = corpus
		self.lems = lems
		self.lem_file = lem_file
		self.sim_algo = sim_algo
		self.prob_word_replace = {'περιΐστημι': 'περιΐστημι',
									'προΐστημι': 'προΐστημι',
									'παρατεινω': 'παρατείνω',
									'μήπως': '',
									'ταβέρνη': 'Ταβέρνη',
									'ἀναμάρτητος': '',
									'προσεγγίζω': '',
									'ηλι': 'ἠλί',
									'δανειστής': 'δανιστής',
									'κατακύπτω':  '',
									'πρωΐ': 'πρωΐ',
									'τυρβάζω': '',
									'Θυάτιρα': 'Θυάτειρα',
									'τετράπουν': 'τετράπους',
									'ἰουδαΐζω': 'ἰουδαΐζω',
									'Τρωγύλλιον': '',
									'σεβαστός': 'Σεβαστός',
									'σωτήριον': 'σωτήριος',
									'κακοπάθεια': 'κακοπαθία',
									'προσανατίθεμαι': 'προσανατίθημι',
									'Χερούβ': 'Χεροῦβ',
									'πρωΐα': 'πρωΐα',
									'Σαλίμ': 'Σαλείμ',
									'νόσημα': '',
									'διΐστημι': 'διΐστημι',
									'Νικολαΐτης': 'Νικολαΐτης',
									'αὐτόφωρος': '',
									'ὅμιλος': '',
									'μαρανα': '',
									'Ματθάτ': 'Ματθάν',
									'ὀρεινή': 'ὀρεινός',
									'δευτερόπρωτος': '',
									'ἔξεστι': 'ἔξεστι(ν)',
									'τομός': 'τομώτερος',
									'πειραω': 'πειράω',
									'ῥυπαίνομαι': 'ῥυπαρεύω',
									'Λεββαιος': '',
									'ελωι': 'ἐλωΐ',
									'πραΰς': 'πραΰς',
									'ὑπερβαίνω': '',
									'ὅποτε': 'ὁπότε',
									'ἐνεός': 'ἐνέος',
									'τεσσαρακονταετής': 'τεσσερακονταετής',
									'ἀγαθοποιΐα': 'ἀγαθοποιΐα',
									'Σάπφειρα': 'Σάπφιρα',
									'σαβαχθανι': 'σαβαχθάνι',
									'στοιχεῖα': 'στοιχεῖον',
									'συζήτησις': '',
									'ἐκτίθεμαι': 'ἐκτίθημι',
									'Κλῆμης': 'Κλήμης',
									'τάραχή': 'τάραχος',
									'Πάρθοι': 'Πάρθος',
									'λεμα': 'λεμά',
									'Λωΐς': 'Λωΐς',
									'Βηθζαθά': 'Βηθεσδά',
									'πίμπραμαι': 'πίμπρημι',
									'Σεμεΐν': 'Σεμεΐν',
									'Νεάπολις': '',
									'Νύμφας': 'Νύμφα',
									'πλείων': 'πολύς',
									'Πτολεμαΐς': 'Πτολεμαΐς',
									'Βηθαβαρα': '',
									'Ῥωμαικος': '',
									'ἐκλανθάνομαι': 'ἐκλανθάνω',
									'Βενιαμείν': 'Βενιαμίν',
									'Ἰουνιᾶς': 'Ἰουνία',
									'πραΰτης': 'πραΰτης',
									'ῥεδή': 'ῥέδη',
									'καταβιβαζω': 'καταβαίνω',
									'σπόριμα': 'σπόριμος',
									'Ἀχαΐα': 'Ἀχαΐα',
									'εὐποιΐα': 'εὐποιΐα',
									'ἀνάτεμα': 'ἀνάθεμα',
									'ὀσφῦς': 'ὀσφύς',
									'κηριον': '',
									'Ναΐν': 'Ναΐν',
									'θα': 'θά',
									'δήποτε': '',
									'θρῆνος': '',
									'Ἠσαΐας': 'Ἠσαΐας',
									'καταγράφω': '',
									'Καλοι Λιμένης': '',
									'πραϋπάθεια': 'πραϋπαθία',
									'τεσσαράκοντα': 'τεσσεράκοντα',
									'μελισσιος': '',
									'Γεργεσηνός': 'Γερασηνός',
									'Ἑβραικός': '',
									'ἅλς': '',
									'Φάρες': 'Φαρές',
									'λόγια': 'λογεία',
									'ἀΐδιος': 'ἀΐδιος',
									'ἀγραύλεω': 'ἀγραυλέω',
									'νεομηνία': 'νουμηνία',
									'Ἑβραΐς': 'Ἑβραΐς',
									'Ἀβραάμ': 'Ἀβραάμ'.lower()}

	def LoadDF(self, w):
		file = '/media/matt/Data/DissProject/Data/SBL_GNT_books/{0}/CS_{1}_{0}_SBL_GNT_books_lems=True_min_occ=None_SVD_exp=1.hd5'.format(str(w), self.algo)
		try:
			self.df = pd.read_hdf(file, 'df')
		except FileNotFoundError:
			file = tk_control("askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format(str(w), 'None'))")
			self.df = pd.read_pickle(file)
		except OSError:
			file = '{3}/{0}/{1}_{8}_{0}_lems={2}_{4}_min_occ={5}_SVD_exp={6}_no_stops=False_weighted={7}.dat'.format(str(w), self.algo, self.lems, self.CS_dir, self.corpus[0], self.corpus[1], self.corpus[2], self.corpus[3], self.sim_algo)
			self.ind = pd.read_pickle('{0}/{2}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops=False.pickle'.format(self.CS_dir, self.corpus[0], str(w), self.lems, self.corpus[1], self.corpus[3]))
			self.df = np.memmap(file, dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))

	def WriteFiles(self):
		with open('{2}/{4}_LN_Word_Cat_Scores_{0}_rng={1}_lems={3}_weighted={5}.pickle'.format(self.algo, self.rng, self.dest_dir, self.lems, self.corpus[0], self.corpus[3]), mode='wb') as file:
			dump(self.scores, file)
		if self.lem_file:
			lems = pd.read_pickle(self.lem_file)
		else:
			lems = {}
		for w_size in self.scores.keys():
			save_file = '{3}/{5}_{7}_LN_Window={0}_Word_Cat_Scores_SVD_exp={1}_{2}_lems={4}_weighted={6}.csv'.format(str(w_size), 'None', self.algo, self.dest_dir, self.lems, self.corpus[0], self.corpus[3], self.sim_algo)
			self.WriteLines(save_file, w_size, 'None', lems)
		with open('{2}/{4}_{6}_LN_Window_Averages_{0}_lems={3}_rng={1}_weighted={5}.pickle'.format(self.algo, self.rng, self.dest_dir, self.lems, self.corpus[0], self.corpus[3], self.sim_algo), mode='wb') as file:
			dump(self.averages, file)
		with open('{2}/{4}_{6}_LN_Window_Averages_{0}_lems={3}_rng={1}_weighted={5}.csv'.format(self.algo, self.rng, self.dest_dir, self.lems, self.corpus[0], self.corpus[3], self.sim_algo),
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window\n')
			file.write('Window Size,Average,+/- Standard Deviations\n')
			for w_size in sorted(self.averages.keys()):
				file.write('{0},{1},{2}\n'.format(w_size, self.averages[w_size][0], self.averages[w_size][1]))
		with open('{2}/{4}_{6}_LN_Window_Averages_no_93_SVD_{0}_lems={3}_rng={1}_weighted={5}.pickle'.format(self.algo, self.rng, self.dest_dir, self.lems, self.corpus[0], self.corpus[3], self.sim_algo), mode='wb') as file:
			dump(self.ave_no_93, file)
		with open('{2}/{4}_{6}_LN_Window_Averages_no_93_SVD_{0}_lems={3}_rng={1}_weighted={5}.csv'.format(self.algo, self.rng, self.dest_dir, self.lems, self.corpus[0], self.corpus[3], self.sim_algo),
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window excluding LN Category 93 (Names)\n')
			file.write('Window Size,Average +/- Standard Deviations\n')
			for w_size in sorted(self.ave_no_93.keys()):
				file.write('{0},{1},{2}\n'.format(w_size, self.ave_no_93[w_size][0], self.ave_no_93[w_size][1]))

class CatSimSVD(CatSim):

	def __init__(self, rng, win, algo):
		'''
		This class calculates the average score for each Louw-Nida category
		based on the SVD exponent that is used.
		:param rng:
		:param win:
		:param algo:
		:return:
		'''
		try:
			self.ln = pd.read_pickle('Data/Chapter_2/LN_Cat_Dict.pickle')
		except FileNotFoundError:
			ln_file = tk_control("askopenfilename(title='Where is your Louw-Nida dictionary pickle?')")
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng_type = 'svd'
		self.rng = rng
		self.win = win
		self.algo = algo
		self.prob_word_replace = {'περιΐστημι': 'περιΐστημι',
									'προΐστημι': 'προΐστημι',
									'παρατεινω': 'παρατείνω',
									'μήπως': '',
									'ταβέρνη': 'Ταβέρνη',
									'ἀναμάρτητος': '',
									'προσεγγίζω': '',
									'ηλι': 'ἠλί',
									'δανειστής': 'δανιστής',
									'κατακύπτω':  '',
									'πρωΐ': 'πρωΐ',
									'τυρβάζω': '',
									'Θυάτιρα': 'Θυάτειρα',
									'τετράπουν': 'τετράπους',
									'ἰουδαΐζω': 'ἰουδαΐζω',
									'Τρωγύλλιον': '',
									'σεβαστός': 'Σεβαστός',
									'σωτήριον': 'σωτήριος',
									'κακοπάθεια': 'κακοπαθία',
									'προσανατίθεμαι': 'προσανατίθημι',
									'Χερούβ': 'Χεροῦβ',
									'πρωΐα': 'πρωΐα',
									'Σαλίμ': 'Σαλείμ',
									'νόσημα': '',
									'διΐστημι': 'διΐστημι',
									'Νικολαΐτης': 'Νικολαΐτης',
									'αὐτόφωρος': '',
									'ὅμιλος': '',
									'μαρανα': '',
									'Ματθάτ': 'Ματθάν',
									'ὀρεινή': 'ὀρεινός',
									'δευτερόπρωτος': '',
									'ἔξεστι': 'ἔξεστι(ν)',
									'τομός': 'τομώτερος',
									'πειραω': 'πειράω',
									'ῥυπαίνομαι': 'ῥυπαρεύω',
									'Λεββαιος': '',
									'ελωι': 'ἐλωΐ',
									'πραΰς': 'πραΰς',
									'ὑπερβαίνω': '',
									'ὅποτε': 'ὁπότε',
									'ἐνεός': 'ἐνέος',
									'τεσσαρακονταετής': 'τεσσερακονταετής',
									'ἀγαθοποιΐα': 'ἀγαθοποιΐα',
									'Σάπφειρα': 'Σάπφιρα',
									'σαβαχθανι': 'σαβαχθάνι',
									'στοιχεῖα': 'στοιχεῖον',
									'συζήτησις': '',
									'ἐκτίθεμαι': 'ἐκτίθημι',
									'Κλῆμης': 'Κλήμης',
									'τάραχή': 'τάραχος',
									'Πάρθοι': 'Πάρθος',
									'λεμα': 'λεμά',
									'Λωΐς': 'Λωΐς',
									'Βηθζαθά': 'Βηθεσδά',
									'πίμπραμαι': 'πίμπρημι',
									'Σεμεΐν': 'Σεμεΐν',
									'Νεάπολις': '',
									'Νύμφας': 'Νύμφα',
									'πλείων': 'πολύς',
									'Πτολεμαΐς': 'Πτολεμαΐς',
									'Βηθαβαρα': '',
									'Ῥωμαικος': '',
									'ἐκλανθάνομαι': 'ἐκλανθάνω',
									'Βενιαμείν': 'Βενιαμίν',
									'Ἰουνιᾶς': 'Ἰουνία',
									'πραΰτης': 'πραΰτης',
									'ῥεδή': 'ῥέδη',
									'καταβιβαζω': 'καταβαίνω',
									'σπόριμα': 'σπόριμος',
									'Ἀχαΐα': 'Ἀχαΐα',
									'εὐποιΐα': 'εὐποιΐα',
									'ἀνάτεμα': 'ἀνάθεμα',
									'ὀσφῦς': 'ὀσφύς',
									'κηριον': '',
									'Ναΐν': 'Ναΐν',
									'θα': 'θά',
									'δήποτε': '',
									'θρῆνος': '',
									'Ἠσαΐας': 'Ἠσαΐας',
									'καταγράφω': '',
									'Καλοι Λιμένης': '',
									'πραϋπάθεια': 'πραϋπαθία',
									'τεσσαράκοντα': 'τεσσεράκοντα',
									'μελισσιος': '',
									'Γεργεσηνός': 'Γερασηνός',
									'Ἑβραικός': '',
									'ἅλς': '',
									'Φάρες': 'Φαρές',
									'λόγια': 'λογεία',
									'ἀΐδιος': 'ἀΐδιος',
									'ἀγραύλεω': 'ἀγραυλέω',
									'νεομηνία': 'νουμηνία',
									'Ἑβραΐς': 'Ἑβραΐς'}

	def LoadDF(self, w):
		file = '/media/matt/Data/DissProject/Data/SBL_GNT_books/{0}/CS_{2}_{0}_SBL_GNT_books_lems=True_min_occ=None_SVD_exp={1}.hd5'.format(self.win, w, self.algo)
		try:
			self.df = pd.read_hdf(file, 'df')
		except FileNotFoundError:
			file = tk_control("askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format('350', w))")
			self.df = pd.read_pickle(file)

	def WriteFiles(self):
		with open('Data/Chapter_2/per_book/LN_Word_Cat_Scores_SVD_{0}.pickle'.format(self.algo), mode='wb') as file:
			dump(self.scores, file)
		lems = pd.read_pickle('Data/SBLGNT_lem_dict.pickle')
		for w_size in self.scores.keys():
			save_file = 'Data/Chapter_2/per_book/LN_Window={0}_Word_Cat_Scores_{2}_SVD_exp={1}.csv'.format(self.win, str(w_size), self.algo)
			self.WriteLines(save_file, '350', w_size, lems)
		with open('Data/Chapter_2/per_book/LN_Window_Averages_SVD_{0}.pickle'.format(self.algo), mode='wb') as file:
			dump(self.averages, file)
		with open('Data/Chapter_2/per_book/LN_Window_Averages_SVD_{0}.csv'.format(self.algo),
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per SVD Exponent\n')
			file.write('SVD Exponent,Average,+/- Standard Deviations\n')
			for w_size in sorted(self.averages.keys()):
				file.write('{0},{1}\n'.format(w_size, self.averages[w_size]))
		with open('Data/Chapter_2/per_book/LN_Window_Averages_no_93_SVD_{0}.pickle'.format(self.algo), mode='wb') as file:
			dump(self.ave_no_93, file)
		with open('Data/Chapter_2/per_book/LN_Window_Averages_no_93_SVD{0}.csv'.format(self.algo),
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
			ln_file = tk_control("askopenfilename(title='Where is your Louw-Nida dictionary pickle?')")
			self.ln = pd.read_pickle(ln_file)
		self.scores = {}
		self.averages = {}
		self.ave_no_93 = {}
		self.good_words = []
		self.prob_words = []
		self.rng = words
		self.prob_word_replace = {'περιΐστημι': 'περιΐστημι',
									'προΐστημι': 'προΐστημι',
									'παρατεινω': 'παρατείνω',
									'μήπως': '',
									'ταβέρνη': 'Ταβέρνη',
									'ἀναμάρτητος': '',
									'προσεγγίζω': '',
									'ηλι': 'ἠλί',
									'δανειστής': 'δανιστής',
									'κατακύπτω':  '',
									'πρωΐ': 'πρωΐ',
									'τυρβάζω': '',
									'Θυάτιρα': 'Θυάτειρα',
									'τετράπουν': 'τετράπους',
									'ἰουδαΐζω': 'ἰουδαΐζω',
									'Τρωγύλλιον': '',
									'σεβαστός': 'Σεβαστός',
									'σωτήριον': 'σωτήριος',
									'κακοπάθεια': 'κακοπαθία',
									'προσανατίθεμαι': 'προσανατίθημι',
									'Χερούβ': 'Χεροῦβ',
									'πρωΐα': 'πρωΐα',
									'Σαλίμ': 'Σαλείμ',
									'νόσημα': '',
									'διΐστημι': 'διΐστημι',
									'Νικολαΐτης': 'Νικολαΐτης',
									'αὐτόφωρος': '',
									'ὅμιλος': '',
									'μαρανα': '',
									'Ματθάτ': 'Ματθάν',
									'ὀρεινή': 'ὀρεινός',
									'δευτερόπρωτος': '',
									'ἔξεστι': 'ἔξεστι(ν)',
									'τομός': 'τομώτερος',
									'πειραω': 'πειράω',
									'ῥυπαίνομαι': 'ῥυπαρεύω',
									'Λεββαιος': '',
									'ελωι': 'ἐλωΐ',
									'πραΰς': 'πραΰς',
									'ὑπερβαίνω': '',
									'ὅποτε': 'ὁπότε',
									'ἐνεός': 'ἐνέος',
									'τεσσαρακονταετής': 'τεσσερακονταετής',
									'ἀγαθοποιΐα': 'ἀγαθοποιΐα',
									'Σάπφειρα': 'Σάπφιρα',
									'σαβαχθανι': 'σαβαχθάνι',
									'στοιχεῖα': 'στοιχεῖον',
									'συζήτησις': '',
									'ἐκτίθεμαι': 'ἐκτίθημι',
									'Κλῆμης': 'Κλήμης',
									'τάραχή': 'τάραχος',
									'Πάρθοι': 'Πάρθος',
									'λεμα': 'λεμά',
									'Λωΐς': 'Λωΐς',
									'Βηθζαθά': 'Βηθεσδά',
									'πίμπραμαι': 'πίμπρημι',
									'Σεμεΐν': 'Σεμεΐν',
									'Νεάπολις': '',
									'Νύμφας': 'Νύμφα',
									'πλείων': 'πολύς',
									'Πτολεμαΐς': 'Πτολεμαΐς',
									'Βηθαβαρα': '',
									'Ῥωμαικος': '',
									'ἐκλανθάνομαι': 'ἐκλανθάνω',
									'Βενιαμείν': 'Βενιαμίν',
									'Ἰουνιᾶς': 'Ἰουνία',
									'πραΰτης': 'πραΰτης',
									'ῥεδή': 'ῥέδη',
									'καταβιβαζω': 'καταβαίνω',
									'σπόριμα': 'σπόριμος',
									'Ἀχαΐα': 'Ἀχαΐα',
									'εὐποιΐα': 'εὐποιΐα',
									'ἀνάτεμα': 'ἀνάθεμα',
									'ὀσφῦς': 'ὀσφύς',
									'κηριον': '',
									'Ναΐν': 'Ναΐν',
									'θα': 'θά',
									'δήποτε': '',
									'θρῆνος': '',
									'Ἠσαΐας': 'Ἠσαΐας',
									'καταγράφω': '',
									'Καλοι Λιμένης': '',
									'πραϋπάθεια': 'πραϋπαθία',
									'τεσσαράκοντα': 'τεσσεράκοντα',
									'μελισσιος': '',
									'Γεργεσηνός': 'Γερασηνός',
									'Ἑβραικός': '',
									'ἅλς': '',
									'Φάρες': 'Φαρές',
									'λόγια': 'λογεία',
									'ἀΐδιος': 'ἀΐδιος',
									'ἀγραύλεω': 'ἀγραυλέω',
									'νεομηνία': 'νουμηνία',
									'Ἑβραΐς': 'Ἑβραΐς'}

	def LoadDF(self):
		file = 'Data/350/PPMI_CS_350_SBL_GNT_SVD_exp=1.45.pickle'
		try:
			self.df = pd.read_pickle(file)
		except FileNotFoundError:
			file = tk_control("askopenfilename(title='Where is your pickle file for window = 350, svd exponent = 1.45')")
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
					new_word = self.prob_word_replace[word]
					if new_word != '':
						cat_words.append((new_word, d[word]))
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

class SynSimWin(CatSimWin):

	def __init__(self, algo, num_syns, rng, syn_file=None, lems=False, CS_dir=None, dest_dir=None, corpus=('SBL_GNT_books', None, 1.0)):
		'''
		This class calculates the context window size that returns the best
		average cosine similarity score based on synonym similarity data
		:param algo:
		:param num_syns:
		:param rng:
		:param syn_file:
		:param lems:
		:return:
		'''
		if syn_file == None:
			syn_file = tk_control("askopenfilename(title='Where is your synonym DF?')")
		try:
			self.syn_df = pd.read_hdf(syn_file, 'CS')
		except:
			self.syn_df = pd.read_pickle(syn_file)
		self.averages = {}
		self.rng = rng
		self.num_syns = num_syns
		self.algo = algo
		self.lems = lems
		self.CS_dir = CS_dir
		self.dest_dir = dest_dir
		self.corpus = corpus

	def LoadDF(self, w):
		#need to implement support for the new .dat (memmap) files I am creating
		file = '{3}/{0}/CS_{1}_{0}_lems={2}_{4}_min_occ={5}_SVD_exp={6}.hd5'.format(str(w), self.algo, self.lems, self.CS_dir, self.corpus[0], self.corpus[1], self.corpus[2])
		try:
			self.df = pd.read_hdf(file, 'df')
		except FileNotFoundError:
			file = tk_control("askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format(str(w), 'None'))")
			self.df = pd.read_pickle(file)
		except OSError:
			file = '{3}/{0}/{1}_CS_{0}_lems={2}_{4}_min_occ={5}_SVD_exp={6}.dat'.format(str(w), self.algo, self.lems, self.CS_dir, self.corpus[0], self.corpus[1], self.corpus[2])
			self.ind = pd.read_pickle('{0}/{2}/{1}_IndexList_w={2}_lems={3}_min_occs={4}.pickle'.format(self.CS_dir, self.corpus[0], str(w), self.lems, self.corpus[1]))
			self.df = np.memmap(file, dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))

	def SimCalc(self, w):
		if self.ind:
			mean, std = np.mean(self.df), np.std(self.df)
		else:
			mean, std = np.mean(self.df.values), np.std(self.df.values)
		print('%s average: %s, std: %s' % (w, mean, std))
		vals = []
		for word in self.top_syns.keys():
			#top_syns = list(self.syn_df[word].order(ascending=False)[1:self.num_syns+1].index)
			for word2 in self.top_syns[word]:
				try:
					if self.ind:
						#this means we are using a memmap and not a DataFrame
						vals.append(self.df[self.ind.index(word)][self.ind.index(word2)])
					else:
						vals.append(self.df.ix[word, word2])
				except KeyError:
					continue
				except ValueError:
					continue
		syn_mean = np.mean(vals)
		syn_std = (np.mean(vals)-mean)/std
		self.averages[w] = (syn_mean, syn_std)

	def WriteFiles(self):
		with open('{4}/{6}_Syn_Window_Averages_{0}_num_syns={1}_lems={3}_rng={2}_min_occs={5}.csv'.format(self.algo,
																										 self.num_syns,
																										 self.rng,
																										 self.lems,
																										 self.dest_dir,
																										 self.corpus[1],
																										 self.corpus[0]),
				  mode='w',
				  encoding='utf-8') as file:
			file.write('Average Number of Standard Deviations above or below Average '
					   'per window\n')
			file.write('Window Size,Average,+/- Standard Deviations\n')
			for w_size in sorted(self.averages.keys()):
				file.write('{0},{1},{2}\n'.format(w_size, self.averages[w_size][0], self.averages[w_size][1]))

	def CatSimPipe(self):
		#calculate the syn list once to speed up later processing
		if type(self.syn_df) == dict:
			self.top_syns = self.syn_df
		else:
			self.top_syns = {}
			for word in self.syn_df.index:
				self.top_syns[word] = list(self.syn_df[word].order(ascending=False)[1:self.num_syns+1].index)
			del self.syn_df
		for w in self.rng:
			self.LoadDF(w)
			self.SimCalc(w)
		self.WriteFiles()
		print('Finished')

class SynSimSVD(SynSimWin):

	def __init__(self, algo, num_syns, rng, win, CS_dir=None, syn_file=None, lems=False):
		'''
		This class calculates the SVD exponent that returns the best
		average cosine similarity score based on synonym similarity data
		:param algo:
		:param num_syns:
		:param rng:
		:param win:
		:param syn_file:
		:param lems:
		:return:
		'''
		if syn_file == None:
			syn_file = tk_control("askopenfilename(title='Where is your synonym DF?')")
		self.syn_df = pd.read_hdf(syn_file, 'CS')
		self.averages = {}
		self.rng = rng
		self.num_syns = num_syns
		self.algo = algo
		self.lems = lems
		self.win = win
		self.CS_dir = CS_dir

	def LoadDF(self, w):
		file = '{4}/{0}/CS_{1}_{0}_SBL_GNT_books_lems={2}_min_occ=None_SVD_exp={3}.hd5'.format(self.win, self.algo, self.lems, str(w), self.CS_dir)
		try:
			self.df = pd.read_hdf(file, 'df')
		except FileNotFoundError:
			file = tk_control("askopenfilename(title='Where is your pickle file for window = {0}, svd exponent = {1}'.format(str(w), 'None'))")
			self.df = pd.read_pickle(file)
