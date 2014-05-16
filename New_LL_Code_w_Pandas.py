'''
To apply the log-likelihood function to every cell in a pandas DataFrame
use df.apply(function).  The function can then call the name and index of
the cell you are working on, and thus call values from other DataFrames
'''
import pandas as pd
import numpy as np
from tkinter.filedialog import askdirectory
import os.path
def file_dict_builder():
    orig_dir = askdirectory(title= 'Where are your collocate DataFrames and lem_dicts located?')
    dest_dir = askdirectory(title = 'Where would you like to save the resulting files?')
    file_list = os.listdir(orig_dir)
    df_dict_dict = {}
    for file in file_list:
        if file.endswith('Coll.pickle'):
            df_dict_dict[file] = ''.join([file.split('.')[0], '_lem_dict.pickle'])
    return df_dict_dict, dest_dir
def log_like(x):
    #The log-likelihood calculator to be called by df.apply()
    c1 = lem_counts[x.name] #the count of the target word (names of the row in the df)
    #In the code below, the following entities map in the following way to the variables in
    #Manning and Schütze (1999) p. 173
    #lem_counts = c2, i.e., the count of the collocate, extracted from the lem_counts series
    #N = N, the total number of words in the corpus
    #c1 = c1, explained above
    #x = c12, the number of co-occurrences of the co-occurrent with the target word, extracted from the Coll_df DataFrame
    #p in Manning & Schütze is lem_counts/N, i.e., the probability of the co-occurrent appearing in the text
    #p1 in Manning & Schütze is x/c1, i.e., the probability of the two words co-occurring given that the target word appears,
    #   i.e., the % of time word 2 occurs out of the total occurrences of word 1
    #p2 in Manning & Schütze is (lem_counts-x)/(N-c1), i.e., the probabilty that word 2 appears outside of co-occurrence with the target word
    L1 = np.log(((lem_counts/N)**c1)*((1-lem_counts/N)**(c1-x)))
    L2 = np.log(((lem_counts/N)**(lem_counts-x))*((1-lem_counts/N)**((N-c1)-lem_counts-x)))
    L3 = np.log(((x/c1)**x)*((1-x/c1)**(c1-x)))
    L4 = np.log((((lem_counts-x)/(N-c1))**(lem_counts-x))*((1-(lem_counts-x)/(N-c1))**((N-c1)-lem_counts-x)))
    LL = L1+L2-L3-L4
    return LL
def counter(lem_dict_filename):
    #constructs a series of the total counts of all of the lemmata from the lem_dict
    #returns this series and N, the total number of words in the corpus
    lem_dict = pd.read_pickle(lem_dict_filename)
    new_dict = {}
    for key, value in lem_dict.values():
        new_dict[key] = value['count']
    lem_counts = pd.Series(new_dict)
    N = lem_counts.sum()
    return lem_counts, N

file_dict, dest_dir = file_dict_builder()
for df_file, lem_file in file_dict.items():
    dest_file = ''.join([dest_dir, df_file.split('_')[0], '_LL.pickle'])
    lem_counts, N = lem_counter(lem_file)
    Coll_df = pd.read_pickle(df_file)
    LL_df = Coll_df.apply(lambda x: log_like(x), axis = 1)
    LL_df.to_pickle(dest_file)
