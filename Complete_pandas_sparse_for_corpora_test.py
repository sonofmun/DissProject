'''
The purpose of this file is to create a new pandas DataFrame from the
np.recarray of each corpus and the sparse DataFrame of the complete LXX lemmas.
This will produce a DataFrame where the values of the original np.array
are still in the frame but the words that are missing are filled in with
nan values.  This will allow the CS similarity calculation between different
corpora
'''
import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
import os
import datetime

orig = askdirectory(title = 'Where are your corpora pickles located?')
full = askopenfilename(title = 'Where is your sparse full lemmata pickle located?')
dest = askdirectory(title = 'Where would you like to save your cosine similarity pickles?')
orig_files = sorted([x for x in os.listdir(orig) if x.endswith('pickle')])
#sparse_list = sorted([x for x in os.listdir(dest) if x.endswith('pickle')])
#file_list = zip(LLlist, sparse_list)

def len_count():
    lem_sparse = pd.read_pickle(full)
    i_to_add = lem_sparse.index - orig_DF.index
    add_df = pd.DataFrame(index = i_to_add, columns = i_to_add)
    return add_df

def join_dfs(orig):
    #This runs into a memory error with the whole LXX file
    #perhaps do it by 1000-row chunks and then concat that into a new file?
    
    return corp_full_DF

for corp in orig_files:
    dest_file = ''.join([dest, '/', corp.split('.')[0], '_full_to_compare.pickle'])
    orig_file = '/'.join([orig, corp])
    if os.path.isfile(dest_file):
        print('%s already exists' % dest_file)
        continue
    else:
        orig_DF = pd.read_pickle(orig_file)
        print('Analyzing %s at %s' % (orig_file, datetime.datetime.now().time().isoformat()))
        DF_to_add = len_count()
        print('Producing combined DF at %s' % datetime.datetime.now().time().isoformat())
        corp_full_sparse = orig_DF.combine_first(DF_to_add)
        print('Producing sparse DF at %s' % datetime.datetime.now().time().isoformat())
        corp_full_sparse = corp_full_sparse.to_sparse()
        print('Saving %s file to pickle at %s' % (dest_file, datetime.datetime.now().time().isoformat()))
        corp_full_sparse.to_pickle(dest_file)
