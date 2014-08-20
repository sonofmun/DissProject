'''
This file will calculate a pandas DataFrame for the co-occurrence of each
word with every other word
'''
import pandas as pd
import re
from tkinter.filedialog import askdirectory
import os.path
from pickle import dump
from collections import defaultdict
import datetime

xml_dir = askdirectory(title = 'Where are your CCAT XML Files located?')
coll_dir = askdirectory(title = 'Where would you like to save your pickled \
                        collocate DataFrames?')
fileslist = os.listdir(xml_dir)

def file_chooser(orig, dest):
    '''
    This function opens the filename from the main for loop, extracts a
    type list and a token list, creates a count dictionary from these two
    lists, and then returns the type and token lists, which will then be
    used to calculated co-occurrences later
    '''
    with open(orig, encoding = 'utf-8') as file:
        filelist = [x.rstrip('\n') for x in file.readlines()]        
    POS = [re.sub(r'.+?ana="([A-Z]).*', r'\1', line) for line in filelist]
    counts = {}
    #NB: looping through list as below is actually faster than using Counter
    for lemma in list(set(POS)):
        counts[lemma] = POS.count(lemma)
    with open(dest, mode = 'wb') as file:
        dump(counts, file)
    return POS

def cooc_counter(tokens, dest, window = 20):
    '''
    This function takes a token list, a windows size (default
    is 20 left and 20 right), and a destination filename, runs through the
    token list, reading every word to the window left and window right of
    the target word, and then keeps track of these co-occurrences in a
    cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from this
    dictionary and then pickles this DataFrame to dest
    '''
    cooc_dict = defaultdict(dict)
    for i, t in enumerate(tokens):
        for pos in range(-window, window+1):
            if pos == 0:
                continue
            else:
                try:
                    cooc_dict[t][i+pos][tokens[i+pos]] += 1
                except:
                    cooc_dict[t][i+pos][tokens[i+pos]] = 1
        ###NEED TO CONTINUE THIS LINE OF THOUGHT
        c_list = []
        [c_list.append(c) for c in
         tokens[max(i-window, 0):min(i+window+1, len(tokens))]]
        c_list.remove(t)
        for c in c_list:
            try:
                cooc_dict[t][c] += 1
            except KeyError:
                cooc_dict[t][c] = 1
        if i % 100000 == 0:
            print('Processing token %s of %s at %s' % (i, len(tokens),
                            datetime.datetime.now().time().isoformat()))
    coll_df = pd.DataFrame(cooc_dict).fillna(0)
    coll_df.to_pickle(dest_file)
    

for filename in fileslist:

    ##########
    '''
    Each loop will open an xml formatted file that contains all of the
    lemmata for a specific document in a 'lemma' attribute for each <w> tag.
    It then derives the name for the destination files for the co-occurrence
    DataFrame and the count dictionary from the input file name for the text
    being analyzed.
    It then calls the function ('file_chooser' defined above) that will
    create the count dictionary and dump it to a pickle file and the type list
    and token list that will be used to create co-occurrence DataFrame.
    Finally, it calls the 'cooc_counter' function, which takes as input
    a token list, a type list, and a window size and finally creates and
    pickles the co-occurrence DataFrame.
    '''
    ##########
    
    print('Now analyzing %s at %s' % (filename, 
                                datetime.datetime.now().time().isoformat()))
    file = '/'.join([xml_dir, filename])
    dest_file = '/'.join([coll_dir, '_'.join([filename.split('_')[1],
                                              'coll.pickle'])])
    dict_file = '/'.join([coll_dir, '_'.join([filename.split('_')[1],
                                              'coll_dict.pickle'])])
    wordlist = file_chooser(file, dict_file)
    cooc_counter(wordlist, dest_file)
        
            
