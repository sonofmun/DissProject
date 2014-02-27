'''
Created on 26.02.2014
by Matthew Munson
The purpose of this script is to create a single nparray with all of any type of given information for every
biblical sub-corpus (LXX and NT as well as the Pentateuch, Former Prophets, Latter Prophets, Writings, and
Intertestamental Literature).  It will be organized according to lemmata with sub-arrays for each corpus
which contain the appropriate scores for each word in relation to the lemma in that corpus.  dtype will look like
dtype=[('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])])])
'''
import numpy as np
from tkinter.filedialog import asksaveasfilename, askopenfilename
#LXX_VSM_File = askopenfilename(title = 'Where is your LXX VSM located?')
PE_VSM_File = askopenfilename(title = 'Where is your PE VSM located?')
#FP_VSM_File = askopenfilename(title = 'Where is your FP VSM located?')
#LP_VSM_File = askopenfilename(title = 'Where is your LP VSM located?')
#WR_VSM_File = askopenfilename(title = 'Where is your WR VSM located?')
#IN_VSM_File = askopenfilename(title = 'Where is your IN VSM located?')
#NT_VSM_File = askopenfilename(title = 'Where is your NT VSM located?')
#Dest_VSM_File = asksaveasfilename(title = 'Where would you like to save your resulting all-corpora VSM file?')
Orig_Files = (LXX_VSM_File, PE_VSM_File, FP_VSM_File, LP_VSM_File, WR_VSM_File, IN_VSM_File, NT_VSM_File)
wordlist = []
for file in Orig_Files:
    with open(file, encoding = 'utf-8') as orig_file:
        headstr = orig_file.readline()
        heading = headstr.replace("'", '').rstrip('\n').split(',')
        for lemma in heading[2:]:
            wordlist.append(lemma.strip())
typelist = sorted(list(set(wordlist))) #creates a list of the types as opposed to the tokens
