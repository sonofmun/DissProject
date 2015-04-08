__author__ = 'matt'

import re
from os.path import splitext
from Data_Production.TK_files import tk_control

gk_files = tk_control("askopenfilenames(title='Where are your Greek source file?')")
#replace the list below with the forms of the word that you want to replace
#putting a \b before and behind all words will make sure the regex matches only
#complete words
words = [r'\bἐκκλησ[ίί]αις\b',
		 r'\bἐκκλησ[ίί]αι\b',
		 r'\bἐκκλησ[ίί]αν\b',
		 r'\bἐκκλησ[ίί]ας\b',
		 r'\bἐκκλησιῶν\b',
		 r'\bἐκκλησ[ίί]ᾳ\b',
		 r'\bἐκκλησ[ίί]αι\b',
		 r'\bἐκκλησ[ίί]α\b',
		 r'\bτἠκκλησ[ίί]ᾳ\b',
		 r'\b[ἐκκλησ[ίί]ας]\b',
		 r'\bἘκκλησ[ίί]αν\b']
#substitute the dictionary form of your lemma below
lemma = 'ἐκκλησία'
for gk_file in gk_files:
	with open(gk_file, mode='r', encoding='utf-8') as f:
		s = f.read()
	p = re.compile(r'({0})'.format('|'.join([w for w in words])))
	s = re.sub(p, lemma, s)
	dest = '{0}_{1}_repl{2}'.format(splitext(gk_file)[0], lemma, splitext(gk_file)[1])
	with open(dest, mode='w', encoding='utf-8') as f:
		f.write(s)