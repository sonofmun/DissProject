import pandas as pd
import numpy as np
def produce_sparse(filename, dest_path):
    '''
    Here, I need to import the column names from one of the LXX np.arrays
    '''
    with open(filename, encoding = 'utf-8') as file:
        lem_list = file.readline().rstrip('\n').replace("'", '').split(', ') #insert here all the things I need to do to clean and split the line
    del lem_list[:2]
    LXX = pd.DataFrame(index = lem_list, columns = lem_list, dtype = float)
    sparse_LXX = LXX.to_sparse()
    sparse_LXX.to_pickle(dest_path)

