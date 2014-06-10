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

orig = askdirectory(title = 'Where are your corpora pickles located?')
full = askopenfilename(title = 'Where is your sparse full lemmata pickle located?')
dest = askdirectory(title = 'Where would you like to save your cosine similarity pickles?')
orig_files = sorted([x for x in os.listdir(orig) if x.endswith('pickle')])
#sparse_list = sorted([x for x in os.listdir(dest) if x.endswith('pickle')])
#file_list = zip(LLlist, sparse_list)

def join_dfs(corp_file):
    print('Opening %s' % corp_file)
    corp_DF = pd.read_pickle(corp_file)
    print('Opening sparse lemma DF')
    lem_sparse = pd.read_pickle(full)
    print('Building new combined DF')
    corp_full_DF = corp_DF.combine_first(lem_sparse).to_sparse()
    return corp_full_DF

for corp in orig_files:
    corp_full_sparse = join_dfs('/'.join([orig, corp]))
    dest_file = ''.join([dest, '/', corp.split('.')[0], '_full_to_compare.pickle'])
    print('Saving %s file to pickle' % dest_file)
    corp_full_sparse.to_pickle(dest_file)
