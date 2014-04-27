import pandas as pd
import numpy as np
def produce_sparse(filename):
    '''
    Here, I need to import the column names from one of the LXX np.arrays
    '''
    with open(filename, encoding = 'utf-8') as file:
        lem_list = file.readline().#insert here all the things I need to do to clean and split the line
    LXX = pd.DataFrame(index = lem_list, columns = lem_list)
    LXX.ix[:] = numpy.nan
    sparse_LXX = LXX.so_sparse()
    sparse_LXX.to_pickle(dest_path)
