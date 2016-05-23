import pandas as pd
import numpy as np
import argparse

def extract_top(i_path, d_path, word, dest_path, top_x=100, **kwargs):
    """ Extracts the top X most similar words to 'word'

    :param i_path: file path and file name for the index file
    :type i_path: str
    :param d_path: file path and file name for the np.memmap containing the data
    :type d_path: str
    :param word: the target word under investigation as represented in the index file (e.g., in Greek letters)
    :type word: str
    :param dest_path: where the resulting CSV containing the X most similar words should be saved
    :type dest_path: str
    :param top_x: the number of most similar words to return
    :type top_x: int
    """
    i = pd.read_pickle(i_path)
    d = np.memmap(d_path, dtype='float', shape=(len(i), len(i)))
    s = pd.Series(d[i.index(word)], index=i)
    s.sort_values(ascending=False).head(top_x).to_csv(dest_path, sep='\t')

def cmd():
    parser = argparse.ArgumentParser(description='Automatic extraction of top X most similar words to the target word.')
    parser.add_argument('--i_path', type=str, help='the full file path and file name for the index file')
    parser.add_argument('--d_path', type=str, help='the full file path and file name for the data file')
    parser.add_argument('--word', type=str,  help='the target word')
    parser.add_argument('--dest_path', type=str, help='the full file path and file name for the resulting CSV file')
    parser.add_argument('--top_x', type=int, default=100, help='the number of most similar words to return')
    parser.add_argument('--occ_dict', type=str,
                        help='The filepath to the file that contains the dictionary of word occurrences')
    parser.add_argument('--min_count', type=int, default=1,
                        help='The minimum number of occurrences for words to be considered in the calculations')
    parser.add_argument('--jobs', type=int, default=1,
                        help='The value for n_jobs in sklearn.metrics.pairwise_distances for cosine similarity calculations')
    parser.add_argument('--no_stops', dest='stops', action='store_false', help='Ignore stop words')
    parser.add_argument('--stops', dest='stops', action='store_true', help='Use stop words')
    parser.set_defaults(func=extract_top)
    args = parser.parse_args()
    args.func(**vars(args))

if __name__== '__main__':
    cmd()