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


class LogLike:

    def __init__(self, colls):
        '''
        To apply the log-likelihood function to every cell in a pandas DataFrame
        use df.apply(function).  The function can then call the name and index of
        the cell you are working on, and thus call values from other DataFrames
        :param colls:
        '''
        self.colls = colls


    def log_L(self, k,n,x):
        '''
        This function applies the correct values from the DataFrame to the
        binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
        '''
        return np.log(np.power(np.float64(x),k)
                      * np.power(np.float64(1-x),n-k))

    def log_space_L(self, k,n,x):
        '''
        This function finds all the inf and -inf values in the Series s and
        corrects the NaN and inf values by moving the whole equation to the log
        space, so that ln((x**k)*(1-x)**(n-k)) = (ln(x)*k) + (ln(1-x)*(n-k))
        I use math.log here instead of np.log because all the values are
        scalars instead of Series and math.log is 10x faster than np.log
        '''
        #I have not implemented this function because it is actually a little
        #slower than running the same loop within the parent function (log_like)

        return np.log(x) * (k) + (np.log(1-x) * (n-k))

    def p_calc(self, c_1, c_2, c_12, n_):
        '''
        This function calculates P1 and P2 for each DataFrame row.
        '''
        p1 = c_12/c_1
        p2 = (c_2-c_12)/(n_-c_1)
        return p1, p2


    def log_like(self, row, C2, P, N):
        '''
        values for c12
        this is the row in the coll_df that I am looking at
        '''
        C12 = self.colls.ix[row]
        #value for C1 will be a scalar value used for all calculations on
        #that row
        C1 = np.sum(C12)
        #The values for P1 and P2 will be the same for the whole row
        #P1, P2 = p_calc(C1, C2, C12, N)
        P1 = C12/C1
        #values for p2
        P2 = (C2-C12)/(N-C1)

        '''
        The following lines call alternately the log_L and the log_space_L
        function.  The first will calculate most values correctly except where
        they underrun the np.float128 object (10**-4950).  Those cases will be
        dealt with by moving the calculations to log space, thus calculating
        the natural log before the float128 can be underrun when taking a
        very small P number to even a moderately large exponent.
        '''

        LL1 = self.log_space_L(C12, C1, P)

        '''
        The following finds all inf and -inf values in LL1 by
        moving calculations into log space.
        '''
        '''
        LL1_inf = LL1[np.isinf(LL1)]
        for ind in LL1_inf.index:
            try:
                LL1.ix[ind] = (log(P[ind])*C12[ind])+\
                              (log(1-P[ind])*(C1-C12[ind]))
            except ValueError as E:
                LL1.ix[ind] = 0
        '''
        LL2 = self.log_space_L(C2-C12, N-C1, P)


        '''
        The following finds all inf and -inf values in LL2 by
        moving calculations into log space.
        '''
        '''
        LL2_inf = LL2[np.isinf(LL2)]
        for ind in LL2_inf.index:
            try:
                LL2.ix[ind] = (log(P[ind])*(C2[ind]-C12[ind]))+\
                              (log(1-P[ind])*((N-C1)-(C2[ind]-C12[ind])))
            except ValueError as E:
                LL2.ix[ind] = 0
        '''
        LL3 = self.log_L(C12, C1, P1)

        '''
        The following finds all inf and -inf values in LL3 by
        moving calculations into log space.
        '''

        LL3_inf = LL3[np.isinf(LL3)]
        for ind in LL3_inf.index:
            try:
                LL3.ix[ind] = (log(P1[ind])*C12[ind])+\
                              (log(1-P1[ind])*(C1-C12[ind]))
            except ValueError as E:
                LL3.ix[ind] = 0

        LL4 = self.log_space_L(C2-C12, N-C1, P2)

        '''
        The following finds all inf and -inf values in LL4 by
        moving calculations into log space.
        '''

        LL4_inf = LL4[np.isinf(LL4)]
        for ind in LL4_inf.index:
            try:
                LL4.ix[ind] = self.log_L((C2[ind]-C12[ind]), (N-C1), P2[ind])
            except ValueError as E:
                LL4.ix[ind] = 0

        return -2 * (LL1 + LL2 - LL3 - LL4)


    def LL(self):
        """Runs a log-likelihood computation on a series of collocation
        DataFrames in a specific directory, saving them to a new directory.
        """

        print('Now running log-likelihood calculations')

        n = np.sum(self.colls.values)
        #values for C2
        c2 = np.sum(self.colls)
        #values for p
        p = c2/n
        LL_df = pd.DataFrame(0., index=self.colls.index,
                             columns=self.colls.index, dtype=np.float64)
        my_counter = 0
        for row in self.colls.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'%
                      (my_counter, len(self.colls),
                       datetime.datetime.now().time().isoformat()))
            LL_df.ix[row] = self.log_like(row, c2, p, n)
            my_counter += 1
        return LL_df.fillna(0)

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

        print('Now running PPMI calculations')

        n = np.sum(self.colls.values)
        #values for C2
        p2 = np.sum(self.colls)/n
        PMI_df = pd.DataFrame(0., index=self.colls.index,
                             columns=self.colls.index, dtype=np.float64)
        my_counter = 0
        for row in self.colls.index:
            if my_counter % 100 == 0:
                print('Row %s of %s at %s'%
                      (my_counter, len(self.colls),
                       datetime.datetime.now().time().isoformat()))
            PMI_df.ix[row] = self.PMI_calc(row, p2, n)
            my_counter += 1
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


def scaler(df):
    """Scales the values of the given DataFrame to a range between
    0 and 1

    :param df:
    """
    from sklearn.preprocessing import MinMaxScaler
    return pd.DataFrame(MinMaxScaler(feature_range=(.01,1)).fit_transform(df))


def SigNoise(df1, df2):
    """Divides the DataFrame representing signal by the DataFrame representing
    noise and returns the sum of the resulting values

    :param df1:
    :param df2:
    :return signal-to-noise ratio:
    """

    return np.mean((df1/df2).values)


def RunTests(min_w, max_w, orig=None):
    now = datetime.datetime.now().time().isoformat()
    if orig == None:
        from tkinter.filedialog import askdirectory
        orig = askdirectory(title='Where are your original XML files located?')
        orig = os.path.join(orig, '*.txt')
    files = glob(orig)
    for file in files:
        corpus = file.split('_')[-2]
        print('Started analyzing %s at %s' % (corpus, now))
        sig_noise_dict = {}
        with open(file) as f:
            t = f.read().split('\n')
        print('Started randomizing at %s' % (now))
        r = randomizer(deepcopy(t))
        for size in range(min_w, max_w+1):
            for lemmata in (True, False):
                for weighted in (True, False):
                    t_colls = CollCount(t, size, lemmata, weighted).colls()
                    r_colls = CollCount(r, size, lemmata, weighted).colls()
                    print('Starting LL calculations for original text for '
                          'window size %s at %s' % (str(size), now))
                    t_ll = LogLike(t_colls).LL()
                    print('Starting LL calculations for randomized text for '
                          'window size %s at %s' % (int(size), now))
                    r_ll = LogLike(r_colls).LL()
                    sig_noise_dict[('LL',
                                    size,
                                    'lems=%s' % (lemmata),
                                    'weighted =%s' % (weighted))] = \
                                    SigNoise(scaler(t_ll),scaler(r_ll))
                    r_ll[r_ll<0] = 0
                    t_ll[t_ll<0] = 0
                    sig_noise_dict[('PLL',
                                    size,
                                    'lems=%s' % (lemmata),
                                    'weighted =%s' % (weighted))] = \
                                    SigNoise(scaler(t_ll),scaler(r_ll))
                    del r_ll, t_ll
                    print('Starting PPMI calculations for original text for '
                          'window size %s at %s' % (str(size), now))
                    t_pmi = PPMI(t_colls).PPMI()
                    print('Starting PPMI calculations for randomized text for '
                          'window size %s at %s' % (int(size), now))
                    r_pmi = PPMI(r_colls).PPMI()
                    sig_noise_dict[('PPMI',
                                    size,
                                    'lems=%s' % (lemmata),
                                    'weighted =%s' % (weighted))] = \
                                    SigNoise(scaler(t_pmi),scaler(r_pmi))
                    del r_pmi, t_pmi
        dest_file = file.replace('.txt', 'sig_noise.pickle')
        with open(dest_file, mode='wb') as f:
            dump(sig_noise_dict, f)
    print('Finished at %s' % (now))

if __name__ == __main__:
    RunTests(1,20, orig=sys.argv[1])