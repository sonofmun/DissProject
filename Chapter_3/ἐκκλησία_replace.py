__author__ = 'matt'

import re
from tkinter.filedialog import askopenfilename
from os.path import splitext

gk_file = askopenfilename(title='Where is your Greek source file?')
with open(gk_file, mode='r', encoding='utf-8') as f:
	s = f.read()
#replace the list below with the forms of the word that you want to replace
#putting a \b before and behind all words will make sure the regex matches only
#complete words
words = [r'\bἐκκλησ[ίί]αις\b', r'\bἐκκλησ[ίί]αι\b', r'\bἐκκλησ[ίί]αν\b', r'\bἐκκλησ[ίί]ας\b', r'\bἐκκλησιῶν\b', r'\bἐκκλησ[ίί]ᾳ\b']
#substitute the dictionary form of your lemma below
lemma = 'ἐκκλησία'
p = re.compile(r'({0})'.format('|'.join([w for w in words])))
s = re.sub(p, lemma, s)
dest = '{0}_{1}_repl{2}'.format(splitext(gk_file)[0], lemma, splitext(gk_file)[1])
with open(dest, mode='w', encoding='utf-8') as f:
	f.write(s)