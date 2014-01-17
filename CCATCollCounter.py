'''
This file will calculate a numpy array for the co-occurrence of each word with every other word
'''
from numpy import *
import re
from tkinter.filedialog import askopenfilename, asksaveasfilename
CCATFile = askopenfilename(title = 'Where is your CCAT XML File located?')
CCATCollFile = asksaveasfilename(title = 'Where would you like to save your file?')
with open(CCATFile, encoding = 'utf-8') as file:
    filelist = [x.rstrip('\n') for x in file.readlines()] #reads all lines of the original file into a list, removing the carriage return in every line
wordlist = [re.sub(r'.+?lem="([^"]*).*', r'\1', line) for line in filelist] #extracts a list of each word used in the text
typelist = sorted(list(set(wordlist))) #creates a list of the types as opposed to the tokens
formats = ['<U30'] #initiates the list that will become the list of the object types of the columns, setting the type of the first column (the target word)
names = ['Lemma', 'Count'] #initiates the list that will become the list of the headings of the columns, calling the first column 'Lemma'
[formats.append('int') for x in range(len(typelist)+1)] #finishes creating the list of column object types, typing them all as floating point depending on the number of lexical types that exist in the original document.
[names.append(x) for x in typelist]  #finishes creating the list of column headings, naming them after the individual lexical types that exist in the document
lemarray = zeros((len(typelist)), {'names': names, 'formats': formats}) #creates an empty array of the size needed typing and naming each column
window = [-4, -3, -2, -1, 1, 2, 3, 4]
'''
the following loop creates the first element in every row, each of which is a lexical type in the original document
the result will be an array that contains a row for every lexical type, which serve as the target words and a column for every lexical
type, which serve as the collocates, and the value in the resulting cell will be the number of co-occurrences of the collocates with the
target word
'''
for x,y in enumerate(typelist): 
    lemarray[x]['Lemma'] = y
    lemarray[x]['Count'] = wordlist.count(y)
for x in range(len(wordlist)):
    lemma = wordlist[x]
    for y in window:
        if x+y < 0:
            continue
        try:
            collocate = wordlist[x+y]
            lemarray[typelist.index(lemma)][collocate] += 1
        except IndexError as E:
            continue
with open(CCATCollFile, mode = 'w', encoding = 'utf-8') as CollFile:
    CollFile.write(''.join([str(lemarray.dtype.names).strip('()'), '\n']))
    for element in range(len(lemarray)):
        CollFile.write(''.join([str(lemarray[element]).strip('()'), '\n']))
        
            
