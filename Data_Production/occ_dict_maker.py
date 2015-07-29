__author__ = 'matt'

from Data_Production.TK_files import tk_control
from glob import glob
import re
from collections import Counter
from pickle import dump

orig = tk_control('askdirectory(title="Where are your original files?")')
files = glob('{0}/*.txt'.format(orig))
words = []
for file in files:
	with open(file) as f:
		lines = f.read().split('\n')
	[words.append(re.sub(r'.+?>([^<]*).*', r'\1', line).lower())
	 for line in lines if re.sub(r'.+?>([^<]*).*', r'\1', line).lower() != '']
occ_dict = Counter(words)
count = len(words)
print('{0} total words, {1} unique words, {2} lexical density'.format(count, len(occ_dict), len(occ_dict)/count))
dest = tk_control('asksaveasfilename(title="Where would you like to save your results?")')
with open(dest, mode='wb') as f:
	dump(occ_dict, f)