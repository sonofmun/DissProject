'''
This file will calculate a numpy array for the co-occurrence of each word with every other word
'''
from numpy import *
import re
with open(r'C:\Users\mam3tc\Documents\GitHub\DissProject\CCAT\CCATUTF-8\39.Micah.mlxx_UTF8.txt', encoding = 'utf-8') as file:
    filelist = [x.strip('\n') for x in file.readlines()]
wordlist = [re.sub(r'[^>]+>([^<]*).*', r'\1', line) for line in filelist]
typelist = sort(list(set(wordlist)))
formats = ['<U30']
names = ['Lemma']
[formats.append('f4') for x in range(len(typelist))]
[names.append(x) for x in typelist]
lemarray = zeros((len(typelist)), {'names': names, 'formats': formats})
for x,y in enumerate(typelist):
    lemarray[x]['Lemma'] = y
