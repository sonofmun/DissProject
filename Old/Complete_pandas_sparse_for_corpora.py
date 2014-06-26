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

def build_part(s, e):
    #this splits the full pickles into 1000-row segments and returns them for merging
    print('Opening rows %s to %s of %s at %s' % (s, e, orig_file, datetime.datetime.now().time().isoformat()))
    c_D_p = pd.read_pickle(orig_file).ix[s:e]
    print('Opening rows %s to %s of %s at %s' % (s, e, full, datetime.datetime.now().time().isoformat()))
    l_s_p = pd.read_pickle(full).ix[s:e]
    print('Combining %s to %s of %s rows at %s' % (s, e, sparse_len, datetime.datetime.now().time().isoformat()))
    return c_D_p.combine_first(l_s_p)
    
def len_count():
    lem_sparse = pd.read_pickle(full)
    sparse_len = len(lem_sparse)
    return sparse_len

def join_dfs():
    #This runs into a memory error with the whole LXX file
    #perhaps do it by 1000-row chunks and then concat that into a new file?
    start = 0
    end = 1000
    while start <= sparse_len:
        print('Now analyzing rows %s to %s at %s' % (start, end, datetime.datetime.now().time().isoformat()))
        corp_full_DF.ix[start:end] = build_part(start, end)
        start = end + 1
        end += 1000
    return corp_full_DF


sparse_len = len_count()
for corp in orig_files:
    dest_file = ''.join([dest, '/', corp.split('.')[0], '_full_to_compare.pickle'])
    orig_file = '/'.join([orig, corp])
    if os.path.isfile(dest_file):
        print('%s already exists' % dest_file)
        continue
    else:
        corp_full_sparse = join_dfs()
        print('Producing sparse DF')
        corp_full_sparse = corp_full_sparse.to_sparse()
        print('Saving %s file to pickle' % dest_file)
        corp_full_sparse.to_pickle(dest_file)
