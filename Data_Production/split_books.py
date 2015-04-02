__author__ = 'matt'

from tkinter.filedialog import askopenfilename, askdirectory
from lxml import etree
from collections import defaultdict
import os

file = askopenfilename(title='Which file would you like to split?')
dest = askdirectory(title='Where would you like to save the resulting files?')
if not os.path.isdir(dest):
	os.mkdir(dest)
with open(file, mode='r', encoding='utf-8') as f:
	lines = f.readlines()
books = defaultdict(list)
l = []
for line in lines:
	book = etree.fromstring(line).get('id').split('.')[0]
	books[book].append(line)
	if book not in l:
		l.append(book)
for b in l:
	with open('{0}/{1}-{2}.txt'.format(dest, l.index(b) + 1, b.replace('/', '-')), mode='w', encoding='utf-8') as f:
		for line in books[b]:
			f.write(line)