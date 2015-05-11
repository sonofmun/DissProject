__author__ = 'matt'

from sklearn.metrics.pairwise import pairwise_distances
import pandas as pd
from Data_Production.TK_files import tk_control

class compare:

	def __init__(self):
		self.base = tk_control('askopenfilename(title="Where is the baseline data?")')
		self.tests = tk_control('askdirectory(title="Where are your division directories?")')
		self.results_s = pd.Series(index=range(10, 201, 10))

	def build_base(self):
		with open(self.base, mode='r', encoding='utf-8') as f:
			base_lines = f.readlines()
		i1 = []
		i2 = []
		v = []
		for line in base_lines:
			a, b, c = line.split()[0], line.split()[1], line.split()[2]
			i1.append(a)
			i2.append(b)
			v.append(c)
		tuples = list(zip(i2, i1))
		i = pd.MultiIndex.from_tuples(tuples, names=['Greek', 'English'])
		self.base_s = pd.Series(v, index=i)

class CS_comp(compare):

	def build_base(self):
		with open(self.base, mode='r', encoding='utf-8') as f:
			base_lines = f.readlines()
		i = []
		v = []
		for line in base_lines:
			a, b = line.split()[:2], line.split()[2]
			i.append(' '.join([a[0], a[1]]))
			v.append(b)
		self.base_s = pd.Series(v, index=i)

	def CS_compare(self):
		for x in range(10, 201, 10):
			print('NOW WORKING ON CHUNK SIZE {0}'.format(x))
			with open('{0}/{1}/lex.f2e'.format(self.tests, x), mode='r', encoding='utf-8') as f:
				test_lines = f.readlines()
			i = []
			v = []
			for line in test_lines:
				a, b = ' '.join([w for w in line.split()[:2]]), line.split()[2]
				i.append(a)
				v.append(b)
			self.test_s = pd.Series(v, index=i)
			df = pd.DataFrame([self.base_s, self.test_s], index=['base', str(x)])
			df = df.fillna(0)
			self.results_s.ix[x] = 1-pairwise_distances(df, metric='cosine')[0, 1]
		self.results_s.to_csv('{0}/results_CS.txt'.format(self.tests))

class best_comp(compare):

	def best_compare(self):
		positive = 0
		total = 0
		for x in range(10, 201, 10):
			print('NOW WORKING ON CHUNK SIZE {0}'.format(x))
			with open('{0}/{1}/lex.f2e'.format(self.tests, x), mode='r', encoding='utf-8') as f:
				test_lines = f.readlines()
			i1 = []
			i2 = []
			v = []
			for line in test_lines:
				a, b, c = line.split()[0], line.split()[1], line.split()[2]
				i1.append(a)
				i2.append(b)
				v.append(c)
			tuples = list(zip(i2, i1))
			i = pd.MultiIndex.from_tuples(tuples, names=['Greek', 'English'])
			self.test_s = pd.Series(v, index=i)
			for word in set(self.base_s.index.get_level_values('Greek')):
				total += 1
				try:
					if self.test_s.ix[word].idxmax() == self.base_s.ix[word].idxmax():
						positive += 1
				except KeyError:
					print('{0} not in test_s'.format(word))
					continue
			self.results_s.ix[x] = positive/total
		self.results_s.to_csv('{0}/results_best.txt'.format(self.tests))

class candidate_comp(compare):

	def cand_compare(self):
		positive = 0
		total = 0
		for x in range(10, 201, 10):
			print('NOW WORKING ON CHUNK SIZE {0}'.format(x))
			with open('{0}/{1}/lex.f2e'.format(self.tests, x), mode='r', encoding='utf-8') as f:
				test_lines = f.readlines()
			i1 = []
			i2 = []
			v = []
			for line in test_lines:
				a, b, c = line.split()[0], line.split()[1], line.split()[2]
				i1.append(a)
				i2.append(b)
				v.append(c)
			tuples = list(zip(i2, i1))
			i = pd.MultiIndex.from_tuples(tuples, names=['Greek', 'English'])
			self.test_s = pd.Series(v, index=i)
			for word in set(self.base_s.index.get_level_values('Greek')):
				for trans in self.base_s[word].index:
					total += 1
					try:
						if trans in self.test_s.ix[word]:
							positive += 1
					except KeyError:
						print('{0} not in test_s'.format(word))
						continue
			self.results_s.ix[x] = positive/total
		self.results_s.to_csv('{0}/results_all_candidates.txt'.format(self.tests))