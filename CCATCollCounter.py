'''
This file will calculate a pandas DataFrame for the co-occurrence of each word with every other word
'''
import pandas as pd
import re
from tkinter.filedialog import askdirectory
import os.path
from pickle import dump

xml_dir = askdirectory(title = 'Where are your CCAT XML Files located?')
coll_dir = askdirectory(title = 'Where would you like to save your pickled collocate DataFrames?')
fileslist = os.listdir(xml_dir)

def file_chooser():
    with open(file, encoding = 'utf-8') as file:
        filelist = [x.rstrip('\n') for x in file.readlines()] #reads all lines of the original file into a list, removing the carriage return in every line
    words = [re.sub(r'.+?lem="([^"]*).*', r'\1', line) for line in filelist] #extracts a list of each word used in the text
    types = sorted(list(set(words))) #creates a list of the types as opposed to the tokens
    counts = {}
    for lemma in types:
        counts[lemma] = words.count(lemma)
    with open(dict_file, mode = 'wb') as file:
        dump(counts, file)
    return types, words


'''
the following loop creates the first element in every row, each of which is a lexical type in the original document
the result will be an array that contains a row for every lexical type, which serve as the target words and a column for every lexical
type, which serve as the collocates, and the value in the resulting cell will be the number of co-occurrences of the collocates with the
target word
'''

window = [-4, -3, -2, -1, 1, 2, 3, 4]
for filename in fileslist:
    print('Now analyzing ', filename)
    file = '/'.join([xml_dir, filename])
    dest_file = '/'.join([coll_dir, '_'.join([filename.split('_')[1], 'coll.pickle'])])
    dict_file = '/'.join([coll_dir, '_'.join([filename.split('_')[1], 'coll_dict.pickle'])])
    type_list, wordlist = file_chooser()
    coll_df = pd.DataFrame(0, index = type_list, columns = type_list)
    N = len(wordlist)

    for x in range(N):
        lemma = wordlist[x]
        for y in window:
            try:
                collocate = wordlist[x+y]
                coll_df.ix[collocate, lemma] += 1
            except IndexError as E:
                continue
        if x % 10000 == 0:
            print(x)
    coll_df.to_pickle(dest_file)
        
            
