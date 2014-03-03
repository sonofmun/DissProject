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
from os.path import split as p_spl
LXX_VSM_File = askopenfilename(title = 'Where is your LXX VSM located?')
PE_VSM_File = askopenfilename(title = 'Where is your PE VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
FP_VSM_File = askopenfilename(title = 'Where is your FP VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
LP_VSM_File = askopenfilename(title = 'Where is your LP VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
WR_VSM_File = askopenfilename(title = 'Where is your WR VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
IN_VSM_File = askopenfilename(title = 'Where is your IN VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
NT_VSM_File = askopenfilename(title = 'Where is your NT VSM located?', initialdir = p_spl(LXX_VSM_File)[0])
Dest_VSM_File = asksaveasfilename(title = 'Where would you like to save your resulting all-corpora VSM file?', initialdir = p_spl(LXX_VSM_File)[0])
Orig_Files = (LXX_VSM_File, PE_VSM_File, FP_VSM_File, LP_VSM_File, WR_VSM_File, IN_VSM_File, NT_VSM_File)
wordlist = []
for file in Orig_Files:
    with open(file, encoding = 'utf-8') as orig_file:
        headstr = orig_file.readline()
        heading = headstr.replace("'", '').rstrip('\n').split(',')
        for lemma in heading[2:]:
            wordlist.append(lemma.strip())
typelist = sorted(list(set(wordlist))) #creates a list of the types as opposed to the tokens
names = ['Lemma', 'Count']
formats = ['<U30', 'int']
for file_1 in Orig_Files: # This loop will fill in the dtype names and formats values for the different corpora comparisons.
    corp_1 = p_spl(file_1)[-1].split('_')[0]
    for file_2 in Orig_Files:
        if file_1 == file_2:
            continue
        else:
            corp_2 = p_spl(file_2)[-1].split('_')[0]
            names.append('-'.join([corp_1, corp_2]))
            formats.append('<f8')
desc_1 = {'names': names, 'formats': formats}
names = ['Lemma', 'Count']
formats = ['<U30', 'int']
[names.append(x) for x in typelist]
[formats.append('int') for x in typelist]
desc_2 = {'names': names, 'formats': formats}
Comp_VSM = np.empty((len(typelist)), dtype = desc_1) #this is the empty array into which the comparison scores between the copora will be put
Comp_VSM[:]['Lemma'] = typelist # sets the value for the 'Lemma' columns of the resulting array
def Txt_to_nparray(orig_file): # this function builds the np.arrays from the txt files
    with open(orig_file, encoding = 'utf-8') as LLfile:
        headstr = LLfile.readline()
        headings = headstr.replace("'", '').rstrip('\n').split(', ')
        formats = ['<U30', 'int']
        [formats.append('int') for x in range(len(headings)-1)]
        mydescriptor = {'names': headings, 'formats': formats}
        print('LLVSM_Temp start')
        LLVSM_Temp = np.loadtxt(LLfile, delimiter = ',', dtype = mydescriptor)
        print(LLVSM_Temp[0][0])
        LLVSM = np.empty((len(headings[2:])), dtype = desc_2)
        print('LLVSM finish')
        LLVSM[:]['Lemma'] = headings[2:]
        for i1, row in enumerate(LLVSM_Temp):
            row = list(row)
            for i, item in enumerate(row[1:]):
                LLVSM[i1][typelist.index(headings[i1+2])] = item
        return LLVSM
LLVSM_1 = Txt_to_nparray(PE_VSM_File)
'''
for file_1 in Orig_Files:
    LLVSM_1 = Txt_to_nparray(file_1)
    for file_2 in Orig_Files:
        if file_1 == file_2:
            continue
        else:
            LLVSM_2 = Txt_to_nparray(file_2)
        
'''
