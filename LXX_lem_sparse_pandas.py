import pandas as pd
import numpy as np
def produce_sparse(LXX_filename, NT_filename, dest_path):
    '''
    Here, I need to import the column names from one of the LXX np.arrays
    '''
    with open(LXX_filename, encoding = 'utf-8') as file:
        LXX_list = file.readline().rstrip('\n').replace("'", '').split(', ') #insert here all the things I need to do to clean and split the line
    with open(NT_filename, encoding = 'utf-8') as file:
        NT_list = file.readline().rstrip('\n').replace("'", '').split(', ')
    del LXX_list[:2]
    del NT_list[:2]
    lem_list = sorted(set(LXX_list).union(set(NT_list)))
    LXX = pd.DataFrame(index = lem_list, columns = lem_list, dtype = float)
    sparse_LXX = LXX.to_sparse()
    sparse_LXX.to_pickle(dest_path)

