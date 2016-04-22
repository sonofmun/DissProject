__author__ = 'matt'

from collections import defaultdict, Counter
import datetime
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances


def counter(weighted, w, words, limits):
    """
    counts the co-occurrences for the words in a certain portion of one file in the corpus
    :param weighted: whether to use a weighted or unweighted window
    :type weighted: bool
    :param w: the context-window size
    :type w: int
    :param words: the list of words in the text
    :type words: list
    :param limits: the beginning and ending indices included in this portion of the file
    :type limits: tuple of ints
    :return: co-occurrence counts for each word that occurs in this portion of the file
    :rtype: collections.Counter
    """
    b, e = limits
    cooc_dict = defaultdict(Counter)
    for i in range(b, e):
        t = words[i]
        c_list = []
        if weighted:
            for pos in range(max(i - w, 0), min(i + w + 1, len(words))):
                if pos != i:
                    for x in range(w + 1 - abs(i - pos)):
                        c_list.append(words[pos])
        else:
            [c_list.append(c) for c in
             words[max(i - w, 0):min(i + w + 1, len(words))]]
            c_list.remove(t)
        cooc_dict[t] += Counter(c_list)
        # for c in c_list:
        # try:
        #		cooc_dict[t][c] += 1
        #	except KeyError:
        #		cooc_dict[t][c] = 1
        if i % 100000 == 0:
            print(
                'Processing token {0} of {1} for window size {2} at {3}'.format(
                    i, len(words), w,
                    datetime.datetime.now().time().isoformat()))
    return Counter(cooc_dict)


def cs_loop(dest_file, stat_file, ind):
    """
        runs the loops over the rows in self.stat_df using numba
        :return:
        :rtype:
        """
    df = np.memmap(dest_file, dtype='float32', mode='w+', shape=(ind, ind))
    stat_df = np.memmap(stat_file, dtype='float32', mode='w+', shape=(ind, ind))
    for i in range(ind):
        df[i] = 1 - pairwise_distances(stat_df[i], stat_df, metric='cosine')
        if i % 5000 == 0:
            del df
            df = np.memmap(dest_file, dtype='float32', mode='r+',
                           shape=(ind, ind))