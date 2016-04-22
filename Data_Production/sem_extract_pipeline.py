#! /usr/bin/env python3

__author__ = 'matt'

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import re
from collections import defaultdict, Counter
import datetime
from math import log, ceil, pow

import pandas as pd
import numpy as np

try:
    from Data_Production.TK_files import tk_control
except ImportError:
    print(
        'Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')
from sklearn.metrics.pairwise import pairwise_distances
from glob import glob
from celery import group
from proj.tasks import counter, svd_calc
from itertools import combinations_with_replacement
from sklearn.cross_validation import KFold
from pickle import dump
from copy import deepcopy
#from multiprocessing import Pool
#from Data_Production.multi_tasks import counter


class SemPipeline:
    def __init__(self, win_size=350, lemmata=True, weighted=True, algo='PPMI',
                 sim_algo='cosine', svd=1, files=None, c=8, occ_dict=None,
                 min_count=1, jobs=1, stops=True):
        """
        This class produces matrices representing cooccurrence counts, statistical significance, and similarity data for a corpus
        :param win_size: context window size
        :type win_size: int
        :param lemmata: whether to use word lemmata
        :type lemmata: bool
        :param weighted: whether to use a weighted window type
        :type weighted: bool
        :param algo: the significance algorithm to use. 'LL' and 'PPMI' are implemented
        :type algo: str
        :param sim_algo: the similarity algorithm to use. 'CS' is implemented
        :type sim_algo: str
        :param svd: the SVD exponent to use (will be removed in the future)
        :type svd: float
        :param files: the directory in which the individual .txt files are held
        :type files: str
        :param c: the number of cores to use in self.cooc_counter (will be removed in the future)
        :type c: int
        :param occ_dict: the path and filename for the occurrence dictionary pickle
        :type occ_dict: str
        :param min_count: the minimum occurrence count below which words will not be counted
        :type min_count: int
        :param jobs: number of jobs to use during the cosine similarity calculations
        :type jobs: int
        :param stops: whether to include stop words or not (True means to include them)
        :type stops: bool
        :return:
        :rtype:
        """
        self.w = win_size
        self.lems = lemmata
        self.weighted = weighted
        self.algo = algo
        if sim_algo in ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
                        'manhattan']:
            self.sim_algo = sim_algo
        else:
            print(
                "The only accepted values for 'sim_algo' are 'cityblock', 'cosine', 'euclidean', 'l1', 'l2', or 'manhattan'")
            print("Setting 'sim_algo' to 'cosine'")
            self.sim_algo = 'cosine'
        if self.algo not in ['PPMI', 'LL', 'both']:
            print(
                'The only accepted values for "algo" are "PPMI", "LL", or "both".')
        self.svd = svd
        self.dir = files
        self.c = c
        if occ_dict == 'None':
            self.occ_dict = None
        else:
            self.occ_dict = occ_dict
        if min_count == 'None':
            self.min_count = None
        else:
            self.min_count = min_count
        self.jobs = jobs
        if stops == False:
            self.stops = ['μή', 'ἑαυτοῦ', 'ἄν', 'ἀλλ’', 'ἀλλά', 'ἄλλος', 'ἀπό',
                          'ἄρα', 'αὐτός', 'δ’', 'δέ', 'δή', 'διά', 'δαί',
                          'δαίς', 'ἔτι', 'ἐγώ', 'ἐκ', 'ἐμός', 'ἐν', 'ἐπί',
                          'εἰ', 'εἰμί', 'εἴμι', 'εἰς', 'γάρ', 'γε', 'γα^', 'ἡ',
                          'ἤ', 'καί', 'κατά', 'μέν', 'μετά', 'μή', 'ὁ', 'ὅδε',
                          'ὅς', 'ὅστις', 'ὅτι', 'οὕτως', 'οὗτος', 'οὔτε',
                          'οὖν',
                          'οὐδείς', 'οἱ', 'οὐ', 'οὐδέ', 'οὐκ', 'περί', 'πρός',
                          'σύ', 'σύν', 'τά', 'τε', 'τήν', 'τῆς', 'τῇ', 'τι',
                          'τί', 'τις', 'τίς', 'τό', 'τοί', 'τοιοῦτος', 'τόν',
                          'τούς', 'τοῦ', 'τῶν', 'τῷ', 'ὑμός', 'ὑπέρ', 'ὑπό',
                          'ὡς', 'ὦ', 'ὥστε', 'ἐάν', 'παρά', 'σός']
        else:
            self.stops = []

    def file_chooser(self):
        """
        uses tkinter.filedialog to fill self.dir if files=None
        :return:
        :rtype:
        """
        if self.dir == None:
            self.dir = tk_control("askdirectory(title='In which directory are the XML file(s) would you like to analyze?')")

    def word_extract(self):
        """
        extracts a list of words from self.t
        :return: list of words
        :rtype: list
        """
        words = []
        if self.lems:
            pattern = re.compile(r'.+?lem="([^"]*).*')
        else:
            pattern = re.compile(r'.+?>([^<]*).*')
        for line in self.t:
            word = re.sub(pattern, r'\1', line).lower()
            if word != '' and word not in self.stops:
                words.append(word)
        return words

    def cooc_counter(self):
        """
        counts the number of times each word co-occurs with each other word
        :return: self.ind - the words that represent the ordered indices of all matrices produced in later calculation
        :rtype: list
        :return: self.coll_df
        :rtype: Numpy memmap
        """
        cooc_dest = os.path.join(self.dest,
                                 '_'.join(['COOC',
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}'.format(
                                               self.weighted)]) + '.dat')
        if os.path.isfile(cooc_dest):
            self.ind = pd.read_pickle(
                '{0}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(
                    self.dest, self.corpus, self.w, self.lems, self.min_count,
                    bool(self.stops)))
            try:
                occs = pd.read_pickle(
                    '{0}/{1}_ColumnList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(
                        self.dest, self.corpus, self.w, self.lems,
                        self.min_count, bool(self.stops)))
                self.cols = len(occs)
            except:
                self.cols = len(self.ind)
            self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r',
                                     shape=(len(self.ind), self.cols))
            return
        counts = Counter()
        if self.occ_dict:
            occs = pd.read_pickle(self.occ_dict)
            min_lems = set([w for w in occs if occs[w] < self.min_count])
            del occs
        else:
            min_lems = set()
        for file in glob('{0}/*.txt'.format(self.dir)):
            with open(file) as f:
                self.t = f.read().split('\n')
            words = self.word_extract()
            step = ceil(len(words) / self.c)
            steps = []
            for i in range(self.c):
                steps.append((step * i, min(step * (i + 1), len(words))))
            self.res = group(
                counter.s(self.weighted, self.w, words, limits) for limits in
                steps)().get()
            #since the counter task returns Counter objects, the update method
            #below adds instead of replacing the values
            for r in self.res:
                for key in r.keys():
                    if key not in min_lems:
                        if key in counts.keys():
                            counts[key].update(r[key])
                        else:
                            counts[key] = r[key]
        self.ind = list(counts.keys())
        try:
            assert (self.col_ind)
        except AttributeError:
            self.col_ind = self.ind
        self.cols = len(self.col_ind)
        with open(
                '{0}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(
                        self.dest, self.corpus, self.w, self.lems,
                        self.min_count, bool(self.stops)), mode='wb') as f:
            dump(self.ind, f)
        with open(
                '{0}/{1}_ColumnList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(
                        self.dest, self.corpus, self.w, self.lems,
                        self.min_count, bool(self.stops)), mode='wb') as f:
            dump(self.col_ind, f)
        print('Now writing cooccurrence file at {0}'.format(
            datetime.datetime.now().time().isoformat()))
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='w+',
                                 shape=(len(self.ind), len(self.col_ind)))
        for i, w in enumerate(self.ind):
            s = pd.Series(counts[w], index=self.col_ind,
                          dtype=np.float64).fillna(0)
            self.coll_df[i] = s.values
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                del self.coll_df
                self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r+',
                                         shape=(
                                             len(self.ind), len(self.col_ind)))
        del self.coll_df
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r',
                                 shape=(len(self.ind), len(self.col_ind)))

    def log_L(self, k, n, x):
        """
        calculates the values for the individual elements of the Log-likelihood equation using the
        binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
        :param k:
        :type k: Pandas Series
        :param n:
        :type n: Numpy ndarray
        :param x:
        :type x: Numpy ndarray
        :return: Log-likelihood values
        :rtype: Numpy ndarray
        """
        return np.log(np.power(np.float64(x), k)
                      * np.power(np.float64(1 - x), n - k))

    def log_space_L(self, k, n, x):
        """
        calculates the values for the individual elements of the Log-likelihood equation using the
        binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
        Moves the calculations to log-space to deal with floats that are too small for float64.
        :param k:
        :type k: Numpy ndarray
        :param n:
        :type n: float
        :param x:
        :type x: Numpy ndarray
        :return: Log-likelihood values
        :rtype: Numpy ndarray
        """
        return np.log(x) * (k) + (np.log(1 - x) * (n - k))

    def log_like(self, row, C2, P, N):
        """
        guides the process of Log-likelihood calculations for a single row
        :param row: the index of the row in the table to be calculated
        :type row: int
        :param C2: number of co-occurrences for each row of the table
        :type C2: Numpy ndarray
        :param P: ratio of co-occurrences per row to total co-occurrences in the table
        :type P: Numpy ndarray
        :param N: total number of co-occurrences in the table
        :type N: float
        :return: Log-likelihood values for a single row in the table
        :rtype: Numpy ndarray
        """
        C12 = self.coll_df[row]
        C1 = np.sum(C12)
        # P1 is ratio of single co-occurrence values to the total co-occurrences for that row
        P1 = C12 / C1
        # P2 ratio of total co-occurrences for a word minus the co-occurrences
        # with the word in question to the total number of co-occurrences in
        # the table minus the total co-occurrences for the row.
        P2 = (C2 - C12) / (N - C1)

        LL1 = self.log_space_L(C12, C1, P)
        LL2 = self.log_space_L(C2 - C12, N - C1, P)
        LL3 = self.log_L(C12, C1, P1)

        # The following finds all inf and -inf values in LL3 by moving calculations into log space.

        LL3_inf = np.where(abs(LL3) == np.inf)
        if len(LL3_inf) > 0:
            for ind in LL3_inf[0]:
                try:
                    LL3[ind] = (log(P1[ind]) * C12[ind]) + (
                        log(1 - P1[ind]) * (C1 - C12[ind]))
                except ValueError:
                    LL3[ind] = 0

        LL4 = self.log_space_L(C2 - C12, N - C1, P2)

        # The following finds all inf and -inf values in LL4 by moving calculations into log space.

        LL4_inf = np.where(abs(LL4) == np.inf)
        if len(LL4_inf) > 0:
            for ind in LL4_inf[0]:
                try:
                    LL4[ind] = self.log_L((C2[ind] - C12[ind]), (N - C1),
                                          P2[ind])
                except ValueError:
                    LL4[ind] = 0

        a = -2 * (LL1 + LL2 - LL3 - LL4)
        a[np.where(np.isfinite(a) == False)] = 0
        return a

    def LL(self):
        """
        guides the Log-likelihood calculations for the whole matrix
        :return: self.LL_df
        :rtype: Numpy memmap
        """
        dest_file = os.path.join(self.dest,
                                 '_'.join(['LL',
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}'.format(
                                               self.weighted)]) + '.dat')
        if os.path.isfile(dest_file):
            self.LL_df = np.memmap(dest_file, dtype='float', mode='r',
                                   shape=(len(self.ind), self.cols))
            return
        n = np.sum(self.coll_df)
        c2 = np.sum(self.coll_df, axis=0)
        p = c2 / n
        self.LL_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(len(self.ind), self.cols))
        for i, w in enumerate(self.ind):
            self.LL_df[i] = self.log_like(i, c2, p, n)
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                del self.LL_df
                self.LL_df = np.memmap(dest_file, dtype='float', mode='r+',
                                       shape=(len(self.ind), self.cols))
        self.LL_df[np.where(np.isfinite(self.LL_df) == False)] = 0
        del self.LL_df
        self.LL_df = np.memmap(dest_file, dtype='float', mode='r',
                               shape=(len(self.ind), self.cols))

    def PMI_calc(self, row, P2, N):
        """
        calculates PPMI values for one table row
        :param row: index for the word's row in the table
        :type row: int
        :param P2: ratio of co-occurrences per row to total co-occurrences in the table
        :type P2: Numpy ndarray
        :param N: total co-occurrences in the table
        :type N: float
        :return: PPMI values for a row in the table
        :rtype: Numpy ndarray
        """
        C12 = self.coll_df[row]
        # C1 is the total co-occurrences in the row
        C1 = np.sum(C12)
        # P1 is the probability that the word co-occurs
        P1 = C1 / N
        # P12 is a vector of the probabilities that the word occurs with any other word
        P12 = C12 / N
        a = np.log2(np.divide(P12, P1 * P2))
        a[np.where(np.isfinite(a) == False)] = 0
        a[a < 0] = 0
        return a

    def PPMI(self):
        """
        guides the PPMI calculation process for the whole table
        :return: matrix of PPMI values
        :rtype: Numpy memmap
        """
        dest_file = os.path.join(self.dest,
                                 '_'.join(['PPMI',
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}'.format(
                                               self.weighted)]) + '.dat')
        if os.path.isfile(dest_file):
            self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r',
                                     shape=(len(self.ind), self.cols))
            return
        n = np.sum(self.coll_df)
        #values for C2
        p2 = np.sum(self.coll_df, axis=0) / n
        self.PPMI_df = np.memmap(dest_file, dtype='float', mode='w+',
                                 shape=(len(self.ind), self.cols))
        for i, w in enumerate(self.ind):
            self.PPMI_df[i] = self.PMI_calc(i, p2, n)
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                del self.PPMI_df
                self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r+',
                                         shape=(len(self.ind), self.cols))
        self.PPMI_df[np.where(np.isfinite(self.PPMI_df) == False)] = 0
        del self.PPMI_df
        self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r',
                                 shape=(len(self.ind), self.cols))

    def CS(self, algorithm, e):
        """
        calculates the cosine similarity of every matrix row with every other row
        :param algorithm: which algorithm (PPMI or LL) is being tested
        :type algorithm: str
        :param e: SVD exponent
        :type e: float
        :return: matrix of cosine similarity values
        :rtype: Numpy memmap
        """
        print('Starting {} calculations for {} for '
              'w={}, lem={}, weighted={} svd={} at {}'.format(self.sim_algo,
                                                              self.corpus,
                                                              str(self.w),
                                                              self.lems,
                                                              self.weighted,
                                                              e,
                                                              datetime.datetime.now().time().isoformat()))
        dest_file = os.path.join(self.dest,
                                 '_'.join([algorithm,
                                           self.sim_algo,
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'SVD_exp={0}'.format(str(e)),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}.dat'.format(
                                               self.weighted)]))
        if os.path.isfile(dest_file):
            return
        if e == 1:
            if algorithm == 'PPMI':
                self.stat_df = self.PPMI_df
                self.stat_file = os.path.join(self.dest,
                                 '_'.join(['PPMI',
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}'.format(
                                               self.weighted)]) + '.dat')
            elif algorithm == 'LL':
                self.stat_df = self.LL_df
                self.stat_file = os.path.join(self.dest,
                                 '_'.join(['LL',
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}'.format(
                                               self.weighted)]) + '.dat')
        else:
            orig = os.path.join(self.dest,
                                '_'.join([algorithm,
                                          'SVD',
                                          str(self.w),
                                          'lems={0}'.format(self.lems),
                                          self.corpus,
                                          'min_occ={0}'.format(self.min_count),
                                          'SVD_exp={0}'.format(str(e)),
                                          'no_stops={0}'.format(
                                              bool(self.stops)),
                                          'weighted={}.dat'.format(
                                              self.weighted)]))
            self.stat_df = np.memmap(orig, dtype='float', mode='r',
                                     shape=(len(self.ind), self.cols))
        self.CS_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(len(self.ind), len(self.ind)))
        '''if self.sim_algo == 'cosine':
            self.CS_df[:] = 1 - pairwise_distances(self.stat_df,
                                                   metric=self.sim_algo,
                                                   n_jobs=self.jobs)
        else:
            self.CS_df[:] = pairwise_distances(self.stat_df,
                                               metric=self.sim_algo,
                                               n_jobs=self.jobs)
        '''
        self.cs_loop(dest_file)
        del self.CS_df
        self.CS_df = np.memmap(dest_file, dtype='float', mode='r',
                               shape=(len(self.ind), len(self.ind)))
        print('Finished with {} calculations for {} for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                       self.corpus,
                                                       str(self.w),
                                                       self.lems,
                                                       self.weighted,
                                                       datetime.datetime.now().time().isoformat()))

    def cs_loop(self, dest_file):
        """
        divides self.stat_df into chunks more easily handled in memory
        (the number of rows use at a time is determined in the step variable)
        and then loops through all chunk combinations
        :param dest_file: the file name to which to save the CS data
        :type dest_file: str
        :return: cosine similarity matrix
        :rtype: np.memmap
        """
        step = 5000
        ind = len(self.ind)
        steps = []
        # steps2 = []
        x = 5000  # 0
        while x < ind:
            steps.append((x - 5000, x))
            # steps2.append(x)
            x += step
        steps.append((steps[-1][-1], ind))
        # steps2.append(ind)
        last_ind = steps[0]
        for i1, i2 in combinations_with_replacement(steps, 2):
            part1 = self.stat_df[i1[0]:i1[1]]
            part2 = self.stat_df[i2[0]:i2[1]]
            self.CS_df[i1[0]:i1[1], i2[0]:i2[1]] = 1- pairwise_distances(part1, part2, metric='cosine')
            self.CS_df[i2[0]:i2[1], i1[0]:i1[1]] = self.CS_df[i1[0]:i1[1], i2[0]:i2[1]].T
            if last_ind != i1:
                print('{0}% done'.format((i1[0] / ind) * 100))
                del self.CS_df
                self.CS_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(ind, ind))
            last_ind = i1
        '''for df_ind in steps:
            part1 = self.stat_df[df_ind:min(df_ind + step, ind)]
            for df_ind2 in steps2:
                part2 = self.stat_df[df_ind2:min(df_ind2 + step, ind)]
                self.CS_df[df_ind:min(df_ind + step, ind), df_ind2:min(df_ind2 + step, ind)] = 1- pairwise_distances(part1, part2, metric='cosine')
            print('{0}% done'.format((df_ind / len(self.ind) * 100)))
            del self.CS_df
            self.CS_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(ind, ind))
        '''

    def stat_eval(self):
        """
        guides the statistical significance calculations required by the parameters given in self.__init__
        :return: None
        :rtype: None
        """
        print('Starting %s calculations for %s for '
              'w=%s, lem=%s, weighted=%s at %s' %
              (self.algo,
               self.corpus,
               str(self.w),
               self.lems,
               self.weighted,
               datetime.datetime.now().time().isoformat()))
        if self.algo == 'both':
            print('Starting PPMI at {0}'.format(os.system('date')))
            self.PPMI()
            print('Starting LL at {0}'.format(os.system('date')))
            self.LL()
        elif self.algo == 'PPMI':
            self.PPMI()
        elif self.algo == 'LL':
            self.LL()
        del self.coll_df
        print('Finished with %s calculations for %s for '
              'w=%s, lem=%s, weighted=%s at %s' %
              (self.algo,
               self.corpus,
               str(self.w),
               self.lems,
               self.weighted,
               datetime.datetime.now().time().isoformat()))

    def svd_calc(self, algorithm):
        """
        calculates the SVD using Caron's exponent
        This function will be removed in future versions.
        :param algorithm: which significance matrix to use (PPMI or LL)
        :type algorithm: str
        :return: matrix transformed with SVD according to Caron's exponent
        :rtype: np.memmap
        """
        print('Starting SVD calculations for %s for '
              'w=%s, lem=%s, weighted=%s at %s' %
              (self.corpus,
               str(self.w),
               self.lems,
               self.weighted,
               datetime.datetime.now().time().isoformat()))
        if algorithm == 'PPMI':
            orig = os.path.join(self.dest,
                                '_'.join(['PPMI',
                                          str(self.w),
                                          'lems={0}'.format(self.lems),
                                          self.corpus,
                                          'min_occ={0}'.format(self.min_count),
                                          'no_stops={0}'.format(
                                              bool(self.stops)),
                                          'weighted={}'.format(
                                              self.weighted)]) + '.dat')
            pause = group(svd_calc.s(orig, os.path.join(self.dest,
                                                        '_'.join([algorithm,
                                                                  'SVD',
                                                                  str(self.w),
                                                                  'lems={0}'.format(
                                                                      self.lems),
                                                                  self.corpus,
                                                                  'min_occ={0}'.format(
                                                                      self.min_count),
                                                                  'SVD_exp={0}'.format(
                                                                      str(e)),
                                                                  'no_stops={0}'.format(
                                                                      bool(
                                                                          self.stops)),
                                                                  'weighted={}.dat'.format(
                                                                      self.weighted)])),
                                     e, (len(self.ind), self.cols)) for e in
                          self.svd)().get()
        elif algorithm == 'LL':
            orig = os.path.join(self.dest,
                                '_'.join(['LL',
                                          str(self.w),
                                          'lems={0}'.format(self.lems),
                                          self.corpus,
                                          'min_occ={0}'.format(self.min_count),
                                          'no_stops={0}'.format(
                                              bool(self.stops)),
                                          'weighted={}'.format(
                                              self.weighted)]) + '.dat')
            pause = group(svd_calc.s(orig, os.path.join(self.dest,
                                                        '_'.join([algorithm,
                                                                  'SVD',
                                                                  str(self.w),
                                                                  'lems={0}'.format(
                                                                      self.lems),
                                                                  self.corpus,
                                                                  'min_occ={0}'.format(
                                                                      self.min_count),
                                                                  'SVD_exp={0}'.format(
                                                                      str(e)),
                                                                  'no_stops={0}'.format(
                                                                      bool(
                                                                          self.stops)),
                                                                  'weighted={}.dat'.format(
                                                                      self.weighted)])),
                                     e, (len(self.ind), self.cols)) for e in
                          self.svd)().get()
        print(pause)
        print('Finished SVD calculations for %s for '
              'w=%s, lem=%s, weighted=%s at %s' %
              (self.corpus,
               str(self.w),
               self.lems,
               self.weighted,
               datetime.datetime.now().time().isoformat()))

    def makeFileNames(self):
        """
        constructs the name of the destination directory and creates the directory if needed
        :return: self.dest
        :rtype: str
        :return: self.corpus
        :rtype: str
        """
        self.dest = os.path.join(self.dir, str(self.w))
        try:
            os.mkdir(self.dest)
        except:
            pass
        self.corpus = self.dir.split('/')[-1]

    def runPipeline(self):
        """
        Guides the whole Pipeline process using the params given in self.__init__
        :return: None
        :rtype: None
        """
        if self.dir == None:
            self.file_chooser()
        self.makeFileNames()
        print('Started analyzing %s at %s' %
              (self.corpus,
               datetime.datetime.now().time().isoformat()))
        self.cooc_counter()
        self.stat_eval()
        if type(self.svd) != list:
            self.svd = [float(self.svd)]
        if self.svd != [1]:
            if self.algo == 'both':
                self.svd_calc('PPMI')
                self.svd_calc('LL')
            elif self.algo == 'PPMI':
                self.svd_calc('PPMI')
            elif self.algo == 'LL':
                self.svd_calc('LL')
        for exp in self.svd:
            if self.algo == 'both':
                self.CS('PPMI', exp)
                self.CS('LL', exp)
            elif self.algo == 'PPMI':
                self.CS('PPMI', exp)
            elif self.algo == 'LL':
                self.CS('LL', exp)

        print('Finished at %s' % (datetime.datetime.now().time().isoformat()))


class ParamTester(SemPipeline):

    def __init__(self, c=8, jobs=1, min_count=1, orig=None):
        """
        runs parameter testing for the corpus in question
        the testing parameters are specified in the self.RunTests function
        :param c: the number of cores to use in the co-occurrence calculations
        :type c: int
        :param jobs: the number of cores to use in the cosine similarity calculations
        :type jobs: int
        :param min_count: the minimum occurrence count. Words below this count will not be counted.
            The purpose here is for memory management. My tests have shown that using all words produces better results.
        :type min_count: int
        :param orig: the directory path for the .txt files that make up the corpus
        :type orig: str
        :return:
        :rtype:
        """
        self.c = c
        self.occ_dict = None
        self.stops = []
        self.jobs = jobs
        self.min_count = min_count
        self.orig = orig
        self.sim_algo = 'CS'

    def cooc_counter(self, files):
        """
        counts the number of times each word co-occurs with each other word
        :return: self.ind - the words that represent the ordered indices of all matrices produced in later calculation
        :rtype: list
        :return: self.coll_df
        :rtype: np.memmap
        """
        counts = Counter()
        if self.occ_dict:
            occs = pd.read_pickle(self.occ_dict)
            min_lems = set([w for w in occs if occs[w] < self.min_count])
            del occs
        else:
            min_lems = set()
        for file in files:
            with open(file) as f:
                self.t = f.read().split('\n')
            words = self.word_extract()
            step = ceil(len(words) / self.c)
            steps = []
            for i in range(self.c):
                steps.append((step * i, min(step * (i + 1), len(words))))
            self.res = group(
                counter.s(self.weighted, self.w, words, limits) for limits in
                steps)().get()
            #since the counter task returns Counter objects, the update method
            #below adds instead of replacing the values
            for r in self.res:
                for key in r.keys():
                    if key not in min_lems:
                        if key in counts.keys():
                            counts[key].update(r[key])
                        else:
                            counts[key] = r[key]
        self.ind = list(counts.keys())
        cooc_dest = '{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems)
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='w+',
                                 shape=(len(self.ind), len(self.ind)))
        for i, w in enumerate(self.ind):
            s = pd.Series(counts[w], index=self.ind,
                          dtype=np.float64).fillna(0)
            self.coll_df[i] = s.values
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                del self.coll_df
                self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r+',
                                         shape=(
                                             len(self.ind), len(self.ind)))
        del self.coll_df
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r',
                                 shape=(len(self.ind), len(self.ind)))
        #return pd.SparseDataFrame.from_dict(counts, orient='index',
        #                                   dtype=np.float64).fillna(0)

    def log_like(self, row, C2, P, N):
        """
        guides the process of Log-likelihood calculations for a single row
        :param row: the index of the row in the table to be calculated
        :type row: int
        :param C2: number of co-occurrences for each row of the table (1-D array)
        :type C2: Numpy ndarray
        :param P: ratio of co-occurrences per row to total co-occurrences in the table (1-D array)
        :type P: Numpy ndarray
        :param N: total number of co-occurrences in the table
        :type N: float
        :return: Log-likelihood values for a single row in the table
        :rtype: Numpy ndarray
        """
        C12 = self.coll_df[row]
        C1 = np.sum(C12)
        # P1 is the ratio of single co-occurrence values to the total co-occurrences for that row
        P1 = C12 / C1
        # P2 is the ratio of total co-occurrences for a word minus the co-occurrences
        # with the word in question to the total number of co-occurrences in
        # the table minus the total co-occurrences for the row.
        P2 = (C2 - C12) / (N - C1)

        LL1 = self.log_space_L(C12, C1, P)

        LL2 = self.log_space_L(C2 - C12, N - C1, P)

        LL3 = self.log_L(C12, C1, P1)

        #The following finds all inf and -inf values in LL3 by moving calculations into log space.

        LL3_inf = np.where(abs(LL3) == np.inf)
        if len(LL3_inf) > 0:
            for ind in LL3_inf[0]:
                try:
                    LL3[ind] = (log(P1[ind]) * C12[ind]) + (
                        log(1 - P1[ind]) * (C1 - C12[ind]))
                except ValueError:
                    LL3[ind] = 0

        LL4 = self.log_space_L(C2 - C12, N - C1, P2)

        #The following finds all inf and -inf values in LL4 by moving calculations into log space.

        LL4_inf = np.where(abs(LL4) == np.inf)
        if len(LL4_inf) > 0:
            for ind in LL4_inf[0]:
                try:
                    LL4[ind] = self.log_L((C2[ind] - C12[ind]), (N - C1),
                                          P2[ind])
                except ValueError:
                    LL4[ind] = 0

        return -2 * (LL1 + LL2 - LL3 - LL4)

    def LL(self):
        """
        guides the Log-likelihood calculations for the whole matrix
        :return: self.LL_df
        :rtype: Numpy memmap
        """
        n = np.sum(self.coll_df)
        c2 = np.sum(self.coll_df, axis=0)
        p = c2 / n
        LL_df = np.memmap('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                          dtype='float', mode='w+',
                          shape=(len(self.ind), len(self.ind)))
        for i, w in enumerate(self.ind):
            LL_df[i] = self.log_like(i, c2, p, n)
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                # deleting LL_df periodically clears the memory of rows that have already been calculated
                del LL_df
                LL_df = np.memmap(
                    '{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                    dtype='float', mode='r+',
                    shape=(len(self.ind), len(self.ind)))
        LL_df[np.where(np.isfinite(LL_df) == False)] = 0
        del LL_df
        LL_df = np.memmap('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                          dtype='float', mode='r',
                          shape=(len(self.ind), len(self.ind)))
        return LL_df

    def PMI_calc(self, row, P2, N):
        """
        calculates PPMI values for one table row
        :param row: index for the word's row in the table
        :type row: int
        :param P2: ratio of co-occurrences per row to total co-occurrences in the table
        :type P2: Numpy ndarray
        :param N: total co-occurrences in the table
        :type N: float
        :return: PPMI values for a row in the table (1-D array)
        :rtype: Numpy ndarray
        """
        C12 = self.coll_df[row]
        C1 = np.sum(C12)
        P1 = C1 / N
        P12 = C12 / N
        a = np.log2(np.divide(P12, P1 * P2))
        a[a < 0] = 0
        return a

    def PPMI(self):
        """
        guides the PPMI calculation process for the whole table
        :return: matrix of PPMI values
        :rtype: Numpy memmap
        """
        n = np.sum(self.coll_df)
        p2 = np.sum(self.coll_df, axis=0) / n
        PPMI_df = np.memmap('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                            dtype='float', mode='w+',
                            shape=(len(self.ind), len(self.ind)))
        for i, w in enumerate(self.ind):
            PPMI_df[i] = self.PMI_calc(i, p2, n)
            if i % 5000 == 0:
                print('{0}% done'.format((i / len(self.ind) * 100)))
                del PPMI_df
                PPMI_df = np.memmap(
                    '{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                    dtype='float', mode='r+',
                    shape=(len(self.ind), len(self.ind)))
        PPMI_df[np.where(np.isfinite(PPMI_df) == False)] = 0
        del PPMI_df
        PPMI_df = np.memmap('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                            dtype='float', mode='r',
                            shape=(len(self.ind), len(self.ind)))
        return PPMI_df

    def CS(self, algorithm, e):
        """
        calculates the cosine similarity of every matrix row with every other row
        :param algorithm: which algorithm (PPMI or LL) is being tested
        :type algorithm: str
        :param e: SVD exponent
        :type e: float
        :return: matrix of cosine similarity values
        :rtype: Numpy memmap
        """
        print('Starting {} calculations for '
              'w={}, lem={}, weighted={} svd={} at {}'.format(self.sim_algo,
                                                              str(self.w),
                                                              self.lems,
                                                              self.weighted,
                                                              e,
                                                              datetime.datetime.now().time().isoformat()))
        dest_file = '{}/{}_{}_{}_CS_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems)
        if e == 1:
            if algorithm == 'PPMI':
                self.stat_df = self.PPMI_df
            elif algorithm == 'LL':
                self.stat_df = self.LL_df
        else:
            orig = os.path.join(self.dest,
                                '_'.join([algorithm,
                                          'SVD',
                                          str(self.w),
                                          'lems={0}'.format(self.lems),
                                          self.corpus,
                                          'min_occ={0}'.format(self.min_count),
                                          'SVD_exp={0}'.format(str(e)),
                                          'no_stops={0}'.format(
                                              bool(self.stops)),
                                          'weighted={}.dat'.format(
                                              self.weighted)]))
            self.stat_df = np.memmap(orig, dtype='float', mode='r',
                                     shape=(len(self.ind), self.cols))
        self.CS_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(len(self.ind), len(self.ind)))
        '''if self.sim_algo == 'cosine':
            self.CS_df[:] = 1 - pairwise_distances(self.stat_df,
                                                   metric=self.sim_algo,
                                                   n_jobs=self.jobs)
        else:
            self.CS_df[:] = pairwise_distances(self.stat_df,
                                               metric=self.sim_algo,
                                               n_jobs=self.jobs)
        '''
        self.cs_loop(dest_file)
        del self.CS_df
        self.CS_df = np.memmap(dest_file, dtype='float', mode='r',
                               shape=(len(self.ind), len(self.ind)))
        print('Finished with {} calculations for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                       str(self.w),
                                                       self.lems,
                                                       self.weighted,
                                                       datetime.datetime.now().time().isoformat()))

    def RunTests(self, min_w, max_w, step, lem_file=None,
                 w_tests='both', l_tests='both'):
        """
        guides the parameter testing process
        :param min_w: the minimum context window size to use
        :type min_w: int
        :param max_w: the maximum context window size to use
        :type max_w: int
        :param step: the size of the steps between min_w and max_w
        :type step: int
        :param lem_file: the path and filename for the word occurrence dictionary pickle
        :type lem_file: str
        :param w_tests: whether to use weighted ("True") or unweighted ("False") window types or "both"
        :type w_tests: str
        :param l_tests: whether to use word lemmas ("True") or inflected forms ("False") or "both"
        :type l_tests: str
        :return:
        :rtype:
        """
        if isinstance(w_tests, str):
            if w_tests == 'both':
                w_tests = (True, False)
            elif w_tests == 'True':
                w_tests = [True]
            elif w_tests == 'False':
                w_tests = [False]
        if isinstance(l_tests, str):
            if l_tests == 'both':
                l_tests = (True, False)
            elif l_tests == 'True':
                l_tests = [True]
            elif l_tests == 'False':
                l_tests = [False]
        if lem_file == 'None':
            lem_file = None
        from Chapter_2.LouwNidaCatSim import CatSimWin

        self.param_dict = {}
        files = glob('{0}/*.txt'.format(self.orig))
        for self.w in range(min_w, max_w + 1, step):
            for self.weighted in w_tests:
                for self.lems in l_tests:
                    prob_list = []
                    pmi_list = []
                    counter = 1
                    print('weighted %s, lemmata %s, w=%s at %s' %
                          (self.weighted,
                           self.lems,
                           self.w,
                           datetime.datetime.now().time().isoformat()))

                    #self.coll_df = self.cooc_counter(files)
                    self.cooc_counter(files)
                    #self.ind = list(self.coll_df.index)
                    self.LL_df = self.LL()
                    #self.coll_df.to_pickle(
                    #    '{}/{}_coll_df.pickle'.format(self.orig, self.w))
                    del self.coll_df
                    pipe = CatSimWin('LL', self.w, lems=self.lems,
                                     CS_dir=self.orig,
                                     dest_dir='{}/Win_size_tests/LN'.format(
                                         self.orig), sim_algo='cosine',
                                     corpus=(self.orig.split('/')[-1], 1, 1.0,
                                             self.weighted), lem_file=lem_file)
                    self.CS('LL', 1)
                    pipe.df = self.CS_df
                    del self.CS_df
                    del self.LL_df
                    pipe.ind = self.ind
                    pipe.SimCalc(self.w)
                    pipe.AveCalc(self.w)
                    pipe.WriteFiles()
                    self.param_dict[
                        'LL_window={}_lems={}_weighted={}'.format(self.w,
                                                                  self.lems,
                                                                  self.weighted)] = \
                        pipe.ave_no_93[self.w]
                    del pipe
                    self.coll_df = np.memmap('{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems), dtype='float', mode='r', shape=(len(self.ind), len(self.ind)))
                    self.PPMI_df = self.PPMI()
                    del self.coll_df
                    pipe = CatSimWin('PPMI', self.w, lems=self.lems,
                                     CS_dir=self.orig,
                                     dest_dir='{}/Win_size_tests/LN'.format(
                                         self.orig), sim_algo='cosine',
                                     corpus=(self.orig.split('/')[-1], 1, 1.0,
                                             self.weighted), lem_file=lem_file)
                    self.CS('PPMI', 1)
                    pipe.df = self.CS_df
                    del self.PPMI_df
                    del self.CS_df
                    pipe.ind = self.ind
                    pipe.SimCalc(self.w)
                    pipe.AveCalc(self.w)
                    pipe.WriteFiles()
                    self.param_dict[
                        'PPMI_window={}_lems={}_weighted={}'.format(self.w,
                                                                    self.lems,
                                                                    self.weighted)] = \
                        pipe.ave_no_93[self.w]
                    del pipe
                    os.remove('{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems))
                    os.remove('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                    os.remove('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                    os.remove('{}/{}_{}_{}_CS_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
            print(self.param_dict)
        dest_file = '{0}/Win_size_tests/{1}_{2}_{3}_weighted={4}_lems={5}.pickle'.format(
            self.orig, os.path.basename(self.orig), min_w, max_w, w_tests,
            l_tests)
        with open(dest_file, mode='wb') as f:
            dump(self.param_dict, f)
        with open(dest_file.replace('.pickle', '.csv'), mode='w') as f:
            f.write('Test Details\tMean Category Score\tCategory Z-Score')
            for k in sorted(self.param_dict.keys(),
                            key=lambda x: int(x.split('_')[1].split('=')[1])):
                f.write('\n{}\t{}\t{}'.format(k, self.param_dict[k][0],
                                              self.param_dict[k][1]))


if __name__ == '__main__':
    if sys.argv[1] == "SemPipeLine":
        SemPipeline(win_size=int(sys.argv[2]),
                    lemmata=bool(int(sys.argv[3])),
                    weighted=bool(int(sys.argv[4])),
                    algo=sys.argv[5],
                    svd=float(sys.argv[6]),
                    files=sys.argv[7],
                    c=int(sys.argv[8]),
                    occ_dict=sys.argv[9],
                    min_count=int(sys.argv[10])).runPipeline()
    if sys.argv[1] == "ParamTester":
        ParamTester(c=int(sys.argv[2]), orig=sys.argv[3],
                    min_count=int(sys.argv[10])).RunTests(min_w=int(sys.argv[4]),
                                                          max_w=int(sys.argv[5]),
                                                          step=int(sys.argv[6]),
                                                          lem_file=sys.argv[7],
                                                          w_tests=sys.argv[8],
                                                          l_tests=sys.argv[9])
