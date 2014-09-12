#! /usr/bin/env python3

__author__ = 'matt'

'''
This file will calculate a pandas DataFrame for the co-occurrence of each
word with every other word
'''
import pandas as pd
import re
import os.path
from pickle import dump
from collections import defaultdict
import datetime
from glob import glob
import numpy as np
from math import log
from copy import deepcopy
import sys


class CollCount:

    def __init__(self, file, w, lem, weighted):
        """Takes an xml formatted file, extracts the 'lem' attributes from
        each <w> tag, and then counts how often each word occurs withing the
        specified window size 'w' left and window size right.
        :param w:
        """
        self.file = file
        self.w = w
        self.lems = lem
        self.weighted = weighted

    def file_chooser(self):
        '''
        This function opens the filename from the main for loop, extracts a
        type list and a token list, creates a count dictionary from these two
        lists, and then returns the type and token lists, which will then be
        used to calculated co-occurrences later
        '''
        if self.lems:
            words = [re.sub(r'.+?lem="([^"]*).*', r'\1', line)
                     for line in self.file]
        else:
            words = [re.sub(r'.+?>([^<]*).*', r'\1', line)
                     for line in self.file]
        return words


    def cooc_counter(self, tokens):
        '''
        This function takes a token list, a windows size (default
        is 4 left and 4 right), and a destination filename, runs through the
        token list, reading every word to the window left and window right of
        the target word, and then keeps track of these co-occurrences in a
        cooc_dict dictionary.  Finally, it creates a coll_df DataFrame from
        this dictionary and then pickles this DataFrame to dest
        '''
        cooc_dict = defaultdict(dict)
        for i, t in enumerate(tokens):
            c_list = []
            if self.weighted:
                for pos in range(max(i-self.w, 0),min(i+self.w+1, len(tokens))):
                    if pos != i:
                        for x in range(self.w+1-abs(i-pos)):
                            c_list.append(tokens[pos])
            else:
                [c_list.append(c) for c in
                 tokens[max(i-self.w, 0):min(i+self.w+1, len(tokens))]]
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
        return coll_df


    def colls(self):
        """Takes an xml formatted file, extracts the 'lem' attributes from
        each <w> tag, and then counts how often each word occurs withing the
        specified window size 'w' left and window size right.
        """

        wordlist = self.file_chooser()
        return self.cooc_counter(wordlist)


class PPMI:

    def __init__(self, colls):
        """Calculates the Positive Pointwise Mutual Information of a
        DataFrame of co-occurrence count values.


        :param colls:
        :return:
        """
        self.colls = colls

    def PMI_calc(self, row, P2, N):
        '''
        values for c12
        this is the row in the coll_df that I am looking at
        '''
        C12 = self.colls.ix[row]
        #value for C1 will be a scalar value used for all calculations on
        #that row
        C1 = np.sum(C12)
        P1 = C1/N
        P12 = C12/N

        return np.log2(np.divide(P12,P1*P2))

    def PPMI(self):
        """Runs a log-likelihood computation on a series of collocation
        DataFrames in a specific directory, saving them to a new directory.
        """


        n = np.sum(self.colls.values)
        #values for C2
        p2 = np.sum(self.colls)/n
        PMI_df = pd.DataFrame(0., index=self.colls.index,
                             columns=self.colls.index, dtype=np.float64)
        for row in self.colls.index:
            PMI_df.ix[row] = self.PMI_calc(row, p2, n)
        PMI_df[PMI_df<0] = 0
        return PMI_df.fillna(0)

'''
class CosSim:

    from sklearn.metrics.pairwise import pairwise_distances

    def __init__(self, LLs):
        """
        Created on 30.04.2013
        by Matthew Munson
        The purpose of this file is to run a cosine similarity comparison between
        every word in the collocation array. The resulting file will be a csv file
        with 1 line for headings, then one line for each lemma, with the CS scores
        for each word in the heading arranged under it.
        :param LLs:
        """
        self.LLs = LLs


    def CS(self):
        """This function calls the pairwise distance function from sklearn
        on every log-likelihood DataFrame in a certain directory and returns
        the similarity score (i.e., 1-cosine distance) for every word, saving
        the results then to a different directory.
        """

        print('Starting cosine similarity calculation at %s' %
              (datetime.datetime.now().time().isoformat()))
        self.LLs = self.LLs.fillna(value=0)
        self.LLs = self.LLs.replace(to_replace=np.inf, value=0)
        CSfile = '_'.join([LLfile.rstrip('_LL.pickle'), 'CS.pickle'])
        #print('test')
        CS_Dists = 1-pairwise_distances(self.LLs, metric='cosine', n_jobs = 1)
        CS = pd.DataFrame(CS_Dists, index=self.LLs.index,
                          columns=self.LLs.index)
        return CS

'''
def randomizer(l):
    """Takes a list of words as input, randomizes the list 1000 times,
    and returns the randomized list.
    """
    from numpy.random import shuffle
    [shuffle(l) for x in range(10)]
    return l


def svd_calc(df, n=1000):
    """Calculates the truncated singular value decomposition of df
    using the first n principal components

    :param df:
    """
    from sklearn.decomposition import TruncatedSVD as t_svd
    return t_svd(n_components=n).fit_transform(df)


def scaler(df):
    """Scales the values of the given DataFrame to a range between
    0 and 1

    :param df:
    """
    from sklearn.preprocessing import MinMaxScaler
    df1 = deepcopy(df)
    return pd.DataFrame(MinMaxScaler(feature_range=(.01,1)).fit_transform(df1))


def SigNoise(df1, df2):
    """Divides the DataFrame representing signal by the DataFrame representing
    noise and returns the sum of the resulting values

    :param df1:
    :param df2:
    :return signal-to-noise ratio:
    """

    return np.mean((df1/df2).values)


def RunTests(min_w, max_w, orig=None):
    if orig == None:
        from tkinter.filedialog import askdirectory
        orig = askdirectory(title='Where are your original XML files located?')
    orig = os.path.join(orig, '*.txt')
    files = glob(orig)
    for file in files:
        corpus = file.split('_')[-2]
        print('Started analyzing %s at %s' %
              (corpus,
              datetime.datetime.now().time().isoformat()))
        sig_noise_dict = {}
        with open(file) as f:
            t = f.read().split('\n')
        print('Started randomizing at %s' %
              (datetime.datetime.now().time().isoformat()))
        r = randomizer(deepcopy(t))
        for size in range(min_w, max_w+1):
            for weighted in (True, False):
                lemmata = True
                t_colls = CollCount(t, size, lemmata, weighted).colls()
                r_colls = CollCount(r, size, lemmata, weighted).colls()
                print('Starting PPMI calculations for original text for '
                      'w=%s, lem=%s, weighted=%s at %s' %
                      (str(size),
                       lemmata,
                       weighted,
                      datetime.datetime.now().time().isoformat()))
                t_pmi = PPMI(t_colls).PPMI()
                t_pmi_svd = svd_calc(t_pmi)
                print('Starting PPMI calculations for randomized text for '
                      'w=%s, lem=%s, weighted=%s at %s' %
                      (str(size),
                       lemmata,
                       weighted,
                      datetime.datetime.now().time().isoformat()))
                r_pmi = PPMI(r_colls).PPMI()
                r_pmi_svd = svd_calc(r_pmi)
                sig_noise_dict[('PPMI',
                                size,
                                'lems=%s' % (lemmata),
                                'weighted =%s' % (weighted))] = \
                                SigNoise(scaler(t_pmi),scaler(r_pmi))
                del r_pmi, t_pmi
                sig_noise_dict[('PPMI_SVD',
                                size,
                                'lems=%s' % (lemmata),
                                'weighted =%s' % (weighted))] = \
                                SigNoise(scaler(t_pmi_svd),scaler(r_pmi_svd))
        dest_file = file.replace('.txt',
                                 '_%s_%s_sig_noise.pickle' % (min_w, max_w))
        with open(dest_file, mode='wb') as f:
            dump(sig_noise_dict, f)
    print('Finished at %s' % (datetime.datetime.now().time().isoformat()))

if __name__ == '__main__':
    if len(sys.argv)>1:
        RunTests(int(sys.argv[1]),int(sys.argv[2]), orig=sys.argv[3])
    else:
        RunTests(1,20)