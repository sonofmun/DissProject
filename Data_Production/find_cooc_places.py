__author__ = 'matt'

from glob import glob
import os
import re

class find_coocs:

	def __init__(self, orig, term, coocs, win_size, dest):
		self.files = glob('{}/*.txt'.format(orig))
		self.term = term
		self.coocs = set(coocs)
		self.win_size = win_size
		self.dest = dest

	def find(self):
		with open(self.dest, mode='w') as dest_file:
			dest_file.write('Filename,Word #,Cooccurrent,Term\n')
			for cooc in self.coocs:
				print(cooc)
				for file in self.files:
					with open(file) as f:
						words = f.read().split('\n')
					for i, word in enumerate(words):
						if self.term in word:
							rng = words[max(0, i-self.win_size):min(len(words), i+self.win_size)]
							for w in rng:
								if cooc in w.lower():
									print(w)
									dest_file.write('{0},{1},{2},{3}\n'.format(os.path.basename(file), i, cooc, word))

class find_forms:

	def __init__(self, orig, regex, dest):
		self.files = glob('{}/*.txt'.format(orig))
		self.pattern = re.compile(r'{}'.format(regex))
		self.dest = dest

	def find(self):
		self.forms = []
		for file in self.files:
			with open(file) as f:
				words = f.read().split('\n')
			for word in words:
				if re.search(self.pattern, word):
					self.forms.append(word)
		with open(self.dest, mode='w') as f:
			for form in sorted(set(self.forms)):
				f.write('{}\n'.format(form))