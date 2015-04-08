__author__ = 'matt'

'''
The purpose of this file is to take the large output files from the Moses
statistical machine translation package and turn them into easily queryable
dictionaries.
'''


from Data_Production.TK_files import tk_control
from collections import defaultdict
from pickle import dump
import pandas as pd

def lex_to_dict():

	file = tk_control('askopenfilename(title="Which Moses lexical file would you like to parse?")')
	dest = tk_control('asksaveasfilename(title="Where would you like to save the pickled dict?")')
	with open(file, mode='r', encoding='utf-8') as f:
		lex_list = f.readlines()
	lex_dict = defaultdict(dict)
	for line in lex_list:
		vals = line.split()
		if len(vals) > 3:
			print('{0} - {1}'.format(lex_list.index(line), line))
		lex_dict[vals[1]][vals[0]] = vals[2]
	with open(dest, mode='wb') as f:
		dump(lex_dict, f)
	return lex_dict

def extract_forms(d, forms, dest, corpus):
	for form in forms:
		pd.Series(d[form]).sort(ascending=False, inplace=False).to_csv('{0}/{1}_{2}.txt'.format(dest, corpus, form))