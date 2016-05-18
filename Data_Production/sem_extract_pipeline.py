#! /usr/bin/env python3

__author__ = 'matt'

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import re
from collections import Counter
import datetime
from math import log, ceil

import pandas as pd
import numpy as np

try:
    from Data_Production.TK_files import tk_control
except ImportError:
    print('Tkinter cannot be used on this Python installation.\nPlease designate a list of files in the files variable.')
from sklearn.metrics.pairwise import pairwise_distances
from glob import glob
# from celery import group
# from proj.tasks import counter, svd_calc
from itertools import combinations_with_replacement
from pickle import dump
from multiprocessing import Pool
from Data_Production.multi_tasks import counter
import argparse


class SemPipeline:
    """ This class produces matrices representing cooccurrence counts, statistical significance, and similarity data for a corpus

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

    :ivar w: the context window size
    :type w: int
    :ivar lems: whether a lemmatized or unlemmatized text will be used
    :type lems: bool
    :ivar weighted: whether a weighted or unweighted context window will be used (True == weighted)
    :type weighted: bool
    :ivar algo: which significance algorithm will be used (PPMI or LL)
    :type algo: str
    :ivar sim_algo: the similarity algorithm to be used
    :type sim_algo: str
    :ivar dir: the directory path in which the texts are located
    :type dir: str
    :ivar c: the number of cores to use during co-occurrence counting
    :type c: int
    :ivar occ_dict: the location for the dictionary representing word counts for every word
    :type occ_dict: str
    :ivar min_count: the minimum threshold of occurrences for the words to be calculated
    :type min_count: int
    :ivar jobs: the value to be used for n_jobs in the cosine similarity calculations
    :type jobs: int
    :ivar stops: a list of stop-words to ignore during the calculations
    :type stops: (str)
    :ivar ind: the indices for the rows and columns of the matrix (i.e., the words) - filled in self.cooc_counter
    :type ind: [str]
    :ivar cols: the length of self.ind - filled in self.cooc_counter
    :ivar cols: int
    :ivar coll_df: transformed into numpy.memmap and filled in self.cooc_counter
    :type coll_df: tuple
    :ivar LL_df: transformed into numpy.memmap and filled in self.LL
    :type LL_df: tuple
    :ivar PPMI_df: transformed into numpy.memmap and filled in self.PPMI
    :type PPMI_df: tuple
    :ivar CS_df: transformed into numpy.memmap and filled in self.CS
    :type CS_df: tuple
    :ivar stat_df: filled with either self.PPMI_df or self.LL_df in self.CS
    :type stat_df: tuple
    :ivar dest: the destination directory for all files - filled in self.makeFileNames
    :type dest: str
    :ivar corpus: the name of the corpus under investigation - filled in self.makeFileNames
    :type corpus: str
    """

    def __init__(self, win_size=350, lemmata=True, weighted=True, algo='PPMI',
                 sim_algo='cosine', files=None, c=8, occ_dict=None,
                 min_count=1, jobs=1, stops=True, **kwargs):
        """ This class produces matrices representing cooccurrence counts, statistical significance, and similarity data for a corpus

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

        :ivar w: the context window size
        :type w: int
        :ivar lems: whether a lemmatized or unlemmatized text will be used
        :type lems: bool
        :ivar weighted: whether a weighted or unweighted context window will be used (True == weighted)
        :type weighted: bool
        :ivar algo: which significance algorithm will be used (PPMI or LL)
        :type algo: str
        :ivar sim_algo: the similarity algorithm to be used
        :type sim_algo: str
        :ivar dir: the directory path in which the texts are located
        :type dir: str
        :ivar c: the number of cores to use during co-occurrence counting
        :type c: int
        :ivar occ_dict: the location for the dictionary representing word counts for every word
        :type occ_dict: str
        :ivar min_count: the minimum threshold of occurrences for the words to be calculated
        :type min_count: int
        :ivar jobs: the value to be used for n_jobs in the cosine similarity calculations
        :type jobs: int
        :ivar stops: a list of stop-words to ignore during the calculations
        :type stops: (str)
        :ivar ind: the indices for the rows and columns of the matrix (i.e., the words) - filled in self.cooc_counter
        :type ind: [str]
        :ivar cols: the length of self.ind - filled in self.cooc_counter
        :ivar cols: int
        :ivar coll_df: transformed into numpy.memmap and filled in self.cooc_counter
        :type coll_df: tuple
        :ivar LL_df: transformed into numpy.memmap and filled in self.LL
        :type LL_df: tuple
        :ivar PPMI_df: transformed into numpy.memmap and filled in self.PPMI
        :type PPMI_df: tuple
        :ivar CS_df: transformed into numpy.memmap and filled in self.CS
        :type CS_df: tuple
        :ivar stat_df: filled with either self.PPMI_df or self.LL_df in self.CS
        :type stat_df: tuple
        :ivar dest: the destination directory for all files - filled in self.makeFileNames
        :type dest: str
        :ivar corpus: the name of the corpus under investigation - filled in self.makeFileNames
        :type corpus: str
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
        if not stops:
            self.stops = ('μή', 'ἑαυτοῦ', 'ἄν', 'ἀλλ’', 'ἀλλά', 'ἄλλος', 'ἀπό',
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
                          'ὡς', 'ὦ', 'ὥστε', 'ἐάν', 'παρά', 'σός')
        else:
            self.stops = ()

        # the following ivars are filled later in the class
        self.ind = []
        self.cols = 0
        self.coll_df = ()
        self.LL_df = ()
        self.PPMI_df = ()
        self.CS_df = ()
        self.stat_df = ()
        self.dest = ''
        self.corpus = ''

    def file_chooser(self):
        """ Uses tkinter.filedialog, as implemented in the tk_control class to fill self.dir if files=None

        """
        self.dir = tk_control("askdirectory(title='In which directory are the XML file(s) would you like to analyze?')")

    def word_extract(self, text, pattern, stops=()):
        """ Extracts a list of words from self.t

        :return: list of words
        :rtype: list
        """
        words = []
        for line in text:
            word = re.sub(pattern, r'\1', line)
            if word != '' and word not in stops:
                words.append(word)
        return words

    def cooc_counter(self):
        """ Counts the number of times each word co-occurs with each other word

        :ivar ind: the words that represent the ordered indices of all matrices produced in later calculation
        :type ind: [int]
        :ivar coll_df: self.coll_df
        :type coll_df: numpy.memmap
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
        # Check to see if a cooccurrence file already exists, if so, exit the method
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

        # Initialize local variables
        counts = Counter()
        if self.lems:
            pattern = re.compile(r'.+?lem="([^"]*).*')
        else:
            pattern = re.compile(r'.+?>([^<]*).*')
        if self.occ_dict:
            occs = pd.read_pickle(self.occ_dict)
            min_lems = set([w for w in occs if occs[w] < self.min_count])
            del occs
        else:
            min_lems = set()

        # Compute co-occurrence counts for each file in self.dir
        for file in glob('{0}/*.txt'.format(self.dir)):
            with open(file) as f:
                words = self.word_extract(f.read().lower().split('\n'), pattern, self.stops)
            step = ceil(len(words) / self.c)
            steps = []
            for i in range(self.c):
                steps.append((step * i, min(step * (i + 1), len(words))))
            '''self.res = group(
                counter.s(self.weighted, self.w, words, limits) for limits in
                steps)().get()
            '''
            #res = []
            with Pool(processes=self.c) as pool:
                #for limits in steps:
                results = pool.starmap(counter, [(self.weighted, self.w, words, limits) for limits in steps])
                    #res.append(results.get())
            #since the counter task returns Counter objects, the update method
            #below adds instead of replacing the values
            for r in results:
                for key in r.keys():
                    if key not in min_lems:
                        if key in counts.keys():
                            counts[key].update(r[key])
                        else:
                            counts[key] = r[key]

        # Fill the ivars that come from the co-occurrence counts
        self.ind = list(counts.keys())
        self.cols = len(self.ind)

        # Write the counts dictionary to a numpy.memmap file
        print('Now writing cooccurrence file at {0}'.format(datetime.datetime.now().time().isoformat()))
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='w+', shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            s = pd.Series(counts[w], index=self.ind,
                          dtype=np.float64).fillna(0)
            self.coll_df[i] = s.values
            if i % 5000 == 0:
                os.system('echo COOC {0}% done'.format((i / self.cols * 100)))
                del self.coll_df
                self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r+',
                                         shape=(
                                             self.cols, self.cols))

        # Re-open self.coll_df as read-only
        del self.coll_df
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r', shape=(self.cols, self.cols))

        # Save the index list and the column list
        with open('{0}/{1}_IndexList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)), mode='wb') as f:
            dump(self.ind, f)
        with open('{0}/{1}_ColumnList_w={2}_lems={3}_min_occs={4}_no_stops={5}.pickle'.format(self.dest, self.corpus, self.w, self.lems, self.min_count, bool(self.stops)), mode='wb') as f:
            dump(self.ind, f)

    def log_L(self, k, n, x):
        """ Calculates the values for the individual elements of the Log-likelihood equation using the
        binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).

        :param k:
        :type k: pandas.Series
        :param n:
        :type n: numpy.ndarray
        :param x:
        :type x: numpy.ndarray
        :return: Log-likelihood values
        :rtype: numpy.ndarray
        """
        return np.log(np.power(np.float64(x), k)
                      * np.power(np.float64(1 - x), n - k))

    def log_space_L(self, k, n, x):
        """ Calculates the values for the individual elements of the Log-likelihood equation using the
        binomial distribution function L(k,n,x) = (x**k)*(1-x)**(n-k).
        Moves the calculations to log-space to deal with floats that are too small for float64.

        :param k:
        :type k: numpy.ndarray
        :param n:
        :type n: float
        :param x:
        :type x: numpy.ndarray
        :return: Log-likelihood values
        :rtype: numpy.ndarray
        """
        return np.log(x) * (k) + (np.log(1 - x) * (n - k))

    def log_like(self, row, C2, P, N):
        """ Guides the process of Log-likelihood calculations for a single row

        :param row: the index of the row in the table to be calculated
        :type row: int
        :param C2: number of co-occurrences for each row of the table
        :type C2: numpy.ndarray
        :param P: ratio of co-occurrences per row to total co-occurrences in the table
        :type P: numpy.ndarray
        :param N: total number of co-occurrences in the table
        :type N: float
        :return: Log-likelihood values for a single row in the table
        :rtype: numpy.ndarray
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
        """ Guides the Log-likelihood calculations for the whole matrix

        :ivar LL_df: matrix of log-likelihood values
        :type LL_df: numpy.memmap
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

        # If a log-likelihood file exists already for these parameters, exit the method
        if os.path.isfile(dest_file):
            self.LL_df = np.memmap(dest_file, dtype='float', mode='r',
                                   shape=(self.cols, self.cols))
            return

        # Initialize local variables
        n = np.sum(self.coll_df)
        c2 = np.sum(self.coll_df, axis=0)
        p = c2 / n

        # Fill self.LL_df with log-likelihood values
        self.LL_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            self.LL_df[i] = self.log_like(i, c2, p, n)
            if i % 5000 == 0:
                os.system('echo LL {0}% done'.format((i / self.cols * 100)))
                del self.LL_df
                self.LL_df = np.memmap(dest_file, dtype='float', mode='r+',
                                       shape=(self.cols, self.cols))

        # Change all numpy.nan and numpy.inf values to 0
        # This is necessary for later calculations that will raise errors for non-finite values
        #self.LL_df[np.where(np.isfinite(self.LL_df) == False)] = 0

        # Dump memory and reload self.LL_df as read-only
        del self.LL_df
        self.LL_df = np.memmap(dest_file, dtype='float', mode='r', shape=(self.cols, self.cols))

    def PMI_calc(self, row, P2, N):
        """ Calculates PPMI values for one table row

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
        """ Guides the PPMI calculation process for the whole table

        :ivar PPMI_df: matrix of PPMI values
        :type PPMI_df: numpy.memmap
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

        # If a PPMI file already exists, exit the method
        if os.path.isfile(dest_file):
            self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r',
                                     shape=(self.cols, self.cols))
            return

        # Initialize local variables
        n = np.sum(self.coll_df)
        #values for C2
        p2 = np.sum(self.coll_df, axis=0) / n

        # Fill self.PPMI_df with values
        self.PPMI_df = np.memmap(dest_file, dtype='float', mode='w+', shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            self.PPMI_df[i] = self.PMI_calc(i, p2, n)
            if i % 5000 == 0:
                os.system('echo PPMI {0}% done'.format((i / self.cols * 100)))
                del self.PPMI_df
                self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r+',
                                         shape=(self.cols, self.cols))

        # Change all numpy.nan and numpy.inf values to 0
        # This is necessary for later calculations that will raise errors for non-finite values
        #self.PPMI_df[np.where(np.isfinite(self.PPMI_df) == False)] = 0

        # Dump memory and reload self.PPMI_df as read-only
        del self.PPMI_df
        self.PPMI_df = np.memmap(dest_file, dtype='float', mode='r',
                                 shape=(self.cols, self.cols))

    def CS(self, algorithm):
        """ Calculates the cosine similarity of every matrix row with every other row

        :param algorithm: which algorithm (PPMI or LL) is being tested
        :type algorithm: str
        :param e: SVD exponent
        :type e: float
        :ivar CS_df: matrix of cosine similarity values
        :type CS_df: numpy.memmap
        """
        print('Starting {} calculations for {} for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                       self.corpus,
                                                       str(self.w),
                                                       self.lems,
                                                       self.weighted,
                                                       datetime.datetime.now().time().isoformat()))
        dest_file = os.path.join(self.dest,
                                 '_'.join([algorithm,
                                           self.sim_algo,
                                           str(self.w),
                                           'lems={0}'.format(self.lems),
                                           self.corpus,
                                           'min_occ={0}'.format(
                                               self.min_count),
                                           'no_stops={0}'.format(
                                               bool(self.stops)),
                                           'weighted={}.dat'.format(
                                               self.weighted)]))
        if os.path.isfile(dest_file):
            return
        if algorithm == 'PPMI':
            self.stat_df = self.PPMI_df
            self.stat_file = os.path.join(self.dest,
                                          '_'.join(
                                              ['PPMI',
                                               str(self.w),
                                               'lems={0}'.format(self.lems),
                                               self.corpus,
                                               'min_occ={0}'.format(self.min_count),
                                               'no_stops={0}'.format(bool(self.stops)),
                                               'weighted={}'.format(self.weighted)]
                                          ) + '.dat')
        elif algorithm == 'LL':
            self.stat_df = self.LL_df
            self.stat_file = os.path.join(self.dest,
                                          '_'.join(
                                              ['LL',
                                               str(self.w),
                                               'lems={0}'.format(self.lems),
                                               self.corpus,
                                               'min_occ={0}'.format(self.min_count),
                                               'no_stops={0}'.format(bool(self.stops)),
                                               'weighted={}'.format(self.weighted)]
                                          ) + '.dat')

        self.CS_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(self.cols, self.cols))
        if self.sim_algo == 'cosine':
            self.CS_df[:] = 1 - pairwise_distances(self.stat_df,
                                                   metric=self.sim_algo,
                                                   n_jobs=self.jobs)
        else:
            self.CS_df[:] = pairwise_distances(self.stat_df,
                                               metric=self.sim_algo,
                                               n_jobs=self.jobs)
        # self.cs_loop(dest_file)
        del self.CS_df
        self.CS_df = np.memmap(dest_file, dtype='float', mode='r', shape=(self.cols, self.cols))
        print('Finished with {} calculations for {} for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                       self.corpus,
                                                       str(self.w),
                                                       self.lems,
                                                       self.weighted,
                                                       datetime.datetime.now().time().isoformat()))

    def cs_loop(self, dest_file):
        """ Divides self.stat_df into chunks more easily handled in memory
        (the number of rows use at a time is determined in the step variable)
        and then loops through all chunk combinations

        :param dest_file: the file name to which to save the CS data
        :type dest_file: str
        """
        step = 5000
        ind = self.cols
        steps = []
        x = step
        while x < ind:
            steps.append((x - step, x))
            x += step
        steps.append((steps[-1][-1], ind))
        last_ind = steps[0]

        for i1, i2 in combinations_with_replacement(steps, 2):
            part1 = self.stat_df[i1[0]:i1[1]]
            part2 = self.stat_df[i2[0]:i2[1]]
            self.CS_df[i1[0]:i1[1], i2[0]:i2[1]] = 1- pairwise_distances(part1, part2, metric='cosine')
            self.CS_df[i2[0]:i2[1], i1[0]:i1[1]] = self.CS_df[i1[0]:i1[1], i2[0]:i2[1]].T
            if last_ind != i1:
                os.system('echo CS {0}% done'.format((i1[0] / ind) * 100))
                del self.CS_df
                self.CS_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(ind, ind))
            last_ind = i1
        '''for df_ind in steps:
            part1 = self.stat_df[df_ind:min(df_ind + step, ind)]
            for df_ind2 in steps2:
                part2 = self.stat_df[df_ind2:min(df_ind2 + step, ind)]
                self.CS_df[df_ind:min(df_ind + step, ind), df_ind2:min(df_ind2 + step, ind)] = 1- pairwise_distances(part1, part2, metric='cosine')
            print('{0}% done'.format((df_ind / self.cols * 100)))
            del self.CS_df
            self.CS_df = np.memmap(dest_file, dtype='float', mode='r+', shape=(ind, ind))
        '''

    def stat_eval(self):
        """ Guides the statistical significance calculations required by the parameters given in self.__init__

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

    def makeFileNames(self):
        """ Constructs the name of the destination directory and creates the directory if needed

        :ivar dest: the directory path into which the results will be saved
        :type dest: str
        :ivar corpus: the name of the corpus being analyzed
        :type corpus: str
        """
        self.dest = os.path.join(self.dir, str(self.w))
        try:
            os.mkdir(self.dest)
        except:
            pass
        self.corpus = self.dir.split('/')[-1]

    def runPipeline(self):
        """ Guides the whole Pipeline process using the params given in self.__init__

        """
        if not self.dir:
            self.file_chooser()
        self.makeFileNames()
        print('Started analyzing %s at %s' %
              (self.corpus,
               datetime.datetime.now().time().isoformat()))
        self.cooc_counter()
        self.stat_eval()
        if self.algo == 'both':
            self.CS('PPMI')
            self.CS('LL')
        elif self.algo == 'PPMI':
            self.CS('PPMI')
        elif self.algo == 'LL':
            self.CS('LL')

        print('Finished at %s' % (datetime.datetime.now().time().isoformat()))


class ParamTester(SemPipeline):
    """ Runs parameter testing for the corpus in question
    the testing parameters are specified in the self.RunTests function

    :param c: the number of cores to use in the co-occurrence calculations
    :type c: int
    :param jobs: the number of cores to use in the cosine similarity calculations
    :type jobs: int
    :param min_count: the minimum occurrence count. Words below this count will not be counted.
        The purpose here is for memory management. My tests have shown that using all words produces better results.
    :type min_count: int
    :param files: the directory path for the .txt files that make up the corpus
    :type files: str
    :param stops: the stops words to be ignored in the calculations
    :type stops: (str)
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
    :param steps: the steps in the calculation process to perform. Allowed: 'all', 'coocs', 'LL', 'PPMI', 'LL_CS' (cosine similarity based on an existing Log-likelihood matrix), or 'PPMI_CS'.
    :type steps: str

    :ivar c: the number of cores to use in the co-occurrence calculations
    :type c: int
    :ivar stops: list of stop words to ignore during the calculations
    :type stops: (str)
    :ivar min_count: the minimum number of occurrences for a word to be used in the calculations
    :type min_count: int
    :ivar files: the directory path for the .txt files that make up the corpus
    :type files: str
    :ivar sim_algo: the similarity algorithm to use in the calculations
    :type sim_algo: str
    :ivar ind: the indices for the rows and columns of the matrix (i.e., the words) - filled in self.cooc_counter
    :type ind: [str]
    :ivar cols: the length of self.ind - filled in self.cooc_counter
    :ivar cols: int
    :ivar coll_df: transformed into numpy.memmap and filled in self.cooc_counter
    :type coll_df: tuple
    :ivar LL_df: transformed into numpy.memmap and filled in self.LL
    :type LL_df: tuple
    :ivar PPMI_df: transformed into numpy.memmap and filled in self.PPMI
    :type PPMI_df: tuple
    :ivar CS_df: transformed into numpy.memmap and filled in self.CS
    :type CS_df: tuple
    :ivar stat_df: filled with either self.PPMI_df or self.LL_df in self.CS
    :type stat_df: tuple
    :ivar param_dict: filled with the scores for each set of parameters in self.RunTests
    :type param_dict: dict
    """

    def __init__(self, min_w, max_w, step, c=8, jobs=1, min_count=1, files=None, stops=tuple(), lem_file=None,
                 w_tests='both', l_tests='both', steps='all', **kwargs):
        """ Runs parameter testing for the corpus in question
        the testing parameters are specified in the self.RunTests function

        :param c: the number of cores to use in the co-occurrence calculations
        :type c: int
        :param jobs: the number of cores to use in the cosine similarity calculations
        :type jobs: int
        :param min_count: the minimum occurrence count. Words below this count will not be counted.
            The purpose here is for memory management. My tests have shown that using all words produces better results.
        :type min_count: int
        :param files: the directory path for the .txt files that make up the corpus
        :type files: str
        :param stops: the stops words to be ignored in the calculations
        :type stops: (str)
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
        :param steps: the steps in the calculation process to perform. Allowed: 'all', 'coocs', 'LL', 'PPMI', 'LL_CS' (cosine similarity based on an existing Log-likelihood matrix), or 'PPMI_CS'.
        :type steps: str

        :ivar c: the number of cores to use in the co-occurrence calculations
        :type c: int
        :ivar stops: list of stop words to ignore during the calculations
        :type stops: (str)
        :ivar min_count: the minimum number of occurrences for a word to be used in the calculations
        :type min_count: int
        :ivar files: the directory path for the .txt files that make up the corpus
        :type files: str
        :ivar sim_algo: the similarity algorithm to use in the calculations
        :type sim_algo: str
        :ivar ind: the indices for the rows and columns of the matrix (i.e., the words) - filled in self.cooc_counter
        :type ind: [str]
        :ivar cols: the length of self.ind - filled in self.cooc_counter
        :ivar cols: int
        :ivar coll_df: transformed into numpy.memmap and filled in self.cooc_counter
        :type coll_df: tuple
        :ivar LL_df: transformed into numpy.memmap and filled in self.LL
        :type LL_df: tuple
        :ivar PPMI_df: transformed into numpy.memmap and filled in self.PPMI
        :type PPMI_df: tuple
        :ivar CS_df: transformed into numpy.memmap and filled in self.CS
        :type CS_df: tuple
        :ivar stat_df: filled with either self.PPMI_df or self.LL_df in self.CS
        :type stat_df: tuple
        :ivar param_dict: filled with the scores for each set of parameters in self.RunTests
        :type param_dict: dict
        """
        self.c = c
        self.stops = stops
        self.jobs = jobs
        self.min_count = min_count
        self.orig = files
        self.sim_algo = 'cosine'
        self.min_w = min_w
        self.max_w = max_w
        self.step = step
        if isinstance(w_tests, str):
            if w_tests == 'both':
                self.w_tests = (True, False)
            elif w_tests == 'True':
                self.w_tests = [True]
            elif w_tests == 'False':
                self.w_tests = [False]
        else:
            self.w_tests = w_tests
        if isinstance(l_tests, str):
            if l_tests == 'both':
                self.l_tests = (True, False)
            elif l_tests == 'True':
                self.l_tests = [True]
            elif l_tests == 'False':
                self.l_tests = [False]
        else:
            self.l_tests = l_tests
        if lem_file == 'None':
            self.lem_file = None
        else:
            self.lem_file = lem_file
        self.do_coocs = False
        self.do_LL = False
        self.do_PPMI = False
        self.do_LL_CS = False
        self.do_PPMI_CS = False
        self.do_all = False
        self.remove = False
        if steps == 'all':
            self.do_coocs = True
            self.do_LL = True
            self.do_PPMI = True
            self.do_LL_CS = True
            self.do_PPMI_CS = True
            self.do_all = True
            self.stat_algos = 'Both'
            self.remove = True
        elif steps == 'coocs':
            self.do_coocs = True
        elif steps == 'LL':
            self.do_LL = True
        elif steps == 'PPMI':
            self.do_PPMI = True
        elif steps == 'LL_CS':
            self.do_LL_CS = True
            self.stat_algos = 'LL'
        elif steps == 'PPMI_CS':
            self.do_PPMI_CS = True
            self.stat_algos = 'PPMI'
        elif steps == 'remove':
            self.remove = True

        # the following ivars are filled later in the class
        self.ind = []
        self.cols = 0
        self.coll_df = ()
        self.LL_df = ()
        self.PPMI_df = ()
        self.CS_df = ()
        self.stat_df = ()
        self.param_dict = {}

    def cooc_counter(self, files):
        """ Counts the number of times each word co-occurs with each other word

        :return: self.ind - the words that represent the ordered indices of all matrices produced in later calculation
        :rtype: list
        :ivar coll_df: the matrix of cooccurrence counts
        :type coll_df: numpy.memmap
        """
        counts = Counter()
        min_lems = set()
        if self.lems:
            pattern = re.compile(r'.+?lem="([^"]*).*')
        else:
            pattern = re.compile(r'.+?>([^<]*).*')
        for file in files:
            with open(file) as f:
                words = self.word_extract(f.read().lower().split('\n'), pattern)
            step = ceil(len(words) / self.c)
            steps = []
            for i in range(self.c):
                steps.append((step * i, min(step * (i + 1), len(words))))
            '''self.res = group(
                counter.s(self.weighted, self.w, words, limits) for limits in
                steps)().get()
            '''
            #res = []
            with Pool(processes=self.c) as pool:
                #for limits in steps:
                results = pool.starmap(counter, [(self.weighted, self.w, words, limits) for limits in steps])
                    #res.append(results.get())
            # since the counter task returns Counter objects, the update method
            # below adds instead of replacing the values
            for r in results:
                for key in r.keys():
                    if key not in min_lems:
                        if key in counts.keys():
                            counts[key].update(r[key])
                        else:
                            counts[key] = r[key]
        self.ind = list(counts.keys())
        self.cols = len(self.ind)  # Need to pickle self.cols for later use
        with open('{}/{}_{}_{}_index.pickle'.format(self.orig, self.w, self.weighted, self.lems), mode='wb') as f:
            dump(self.ind, f)
        cooc_dest = '{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems)
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='w+',
                                 shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            s = pd.Series(counts[w], index=self.ind,
                          dtype=np.float64).fillna(0)
            self.coll_df[i] = s.values
            if i % 5000 == 0:
                os.system('echo COOC {0}% done'.format((i / self.cols * 100)))
                del self.coll_df
                self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r+',
                                         shape=(
                                             self.cols, self.cols))
        del self.coll_df
        self.coll_df = np.memmap(cooc_dest, dtype='float', mode='r',
                                 shape=(self.cols, self.cols))

    def log_like(self, row, C2, P, N):
        """ Guides the process of Log-likelihood calculations for a single row

        :param row: the index of the row in the table to be calculated
        :type row: int
        :param C2: number of co-occurrences for each row of the table (1-D array)
        :type C2: numpy.ndarray
        :param P: ratio of co-occurrences per row to total co-occurrences in the table (1-D array)
        :type P: numpy.ndarray
        :param N: total number of co-occurrences in the table
        :type N: float
        :return: Log-likelihood values for a single row in the table
        :rtype: numpy.ndarray
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
        """ Guides the Log-likelihood calculations for the whole matrix

        :return: self.LL_df
        :rtype: numpy.memmap
        """
        n = np.sum(self.coll_df)
        c2 = np.sum(self.coll_df, axis=0)
        p = c2 / n
        LL_df = np.memmap('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                          dtype='float', mode='w+',
                          shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            LL_df[i] = self.log_like(i, c2, p, n)
            if i % 5000 == 0:
                os.system('echo LL {0}% done'.format((i / self.cols * 100)))
                # deleting LL_df periodically clears the memory of rows that have already been calculated
                del LL_df
                LL_df = np.memmap(
                    '{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                    dtype='float', mode='r+',
                    shape=(self.cols, self.cols))
        #LL_df[np.where(np.isfinite(LL_df) == False)] = 0
        del LL_df
        '''LL_df = np.memmap('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                          dtype='float', mode='r',
                          shape=(self.cols, self.cols))
        return LL_df
        '''

    def PMI_calc(self, row, P2, N):
        """ Calculates PPMI values for one table row

        :param row: index for the word's row in the table
        :type row: int
        :param P2: ratio of co-occurrences per row to total co-occurrences in the table
        :type P2: numpy.ndarray
        :param N: total co-occurrences in the table
        :type N: float
        :return: PPMI values for a row in the table (1-D array)
        :rtype: numpy.ndarray
        """
        C12 = self.coll_df[row]
        C1 = np.sum(C12)
        P1 = C1 / N
        P12 = C12 / N
        a = np.log2(np.divide(P12, P1 * P2))
        a[a < 0] = 0
        return a

    def PPMI(self):
        """ Guides the PPMI calculation process for the whole table

        :return: matrix of PPMI values
        :rtype: numpy.memmap
        """
        n = np.sum(self.coll_df)
        p2 = np.sum(self.coll_df, axis=0) / n
        PPMI_df = np.memmap('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                            dtype='float', mode='w+',
                            shape=(self.cols, self.cols))
        for i, w in enumerate(self.ind):
            PPMI_df[i] = self.PMI_calc(i, p2, n)
            if i % 5000 == 0:
                os.system('echo PPMI {0}% done'.format((i / self.cols * 100)))
                del PPMI_df
                PPMI_df = np.memmap(
                    '{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                    dtype='float', mode='r+',
                    shape=(self.cols, self.cols))
        #PPMI_df[np.where(np.isfinite(PPMI_df) == False)] = 0
        del PPMI_df
        '''PPMI_df = np.memmap('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems),
                            dtype='float', mode='r',
                            shape=(self.cols, self.cols))
        return PPMI_df
        '''

    def CS(self, algorithm):
        """ Calculates the cosine similarity of every matrix row with every other row

        :param algorithm: which algorithm (PPMI or LL) is being tested
        :type algorithm: str
        :param e: SVD exponent
        :type e: float
        :ivar CS_df: matrix of cosine similarity values
        :type CS_df: numpy.memmap
        """
        print('Starting {} calculations for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                              str(self.w),
                                                              self.lems,
                                                                 self.weighted,
                                                              datetime.datetime.now().time().isoformat()))
        dest_file = '{}/{}_{}_{}_{}_CS_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems, algorithm)

        if algorithm == 'PPMI':
            self.stat_df = self.PPMI_df
        elif algorithm == 'LL':
            self.stat_df = self.LL_df

        self.CS_df = np.memmap(dest_file, dtype='float', mode='w+',
                               shape=(self.cols, self.cols))
        if self.sim_algo == 'cosine':
            self.CS_df[:] = 1 - pairwise_distances(self.stat_df,
                                                   metric=self.sim_algo,
                                                   n_jobs=self.jobs)
        else:
            self.CS_df[:] = pairwise_distances(self.stat_df,
                                               metric=self.sim_algo,
                                               n_jobs=self.jobs)
        # self.cs_loop(dest_file)
        del self.CS_df
        self.CS_df = np.memmap(dest_file, dtype='float', mode='r',
                               shape=(self.cols, self.cols))
        print('Finished with {} calculations for '
              'w={}, lem={}, weighted={} at {}'.format(self.sim_algo,
                                                       str(self.w),
                                                       self.lems,
                                                       self.weighted,
                                                       datetime.datetime.now().time().isoformat()))

    def RunTests(self):
        """ Guides the parameter testing process
        """
        from Chapter_2.LouwNidaCatSim import CatSimWin

        files = glob('{0}/*.txt'.format(self.orig))
        for self.w in range(self.min_w, self.max_w + 1, self.step):
            for self.weighted in self.w_tests:
                for self.lems in self.l_tests:
                    print('weighted %s, lemmata %s, w=%s at %s' %
                          (self.weighted,
                           self.lems,
                           self.w,
                           datetime.datetime.now().time().isoformat()))

                    if self.do_coocs:
                        self.cooc_counter(files)
                    if not self.ind:
                        self.ind = pd.read_pickle('{}/{}_{}_{}_index.pickle'.format(self.orig, self.w, self.weighted, self.lems))
                        self.cols = len(self.ind)
                    self.coll_df = np.memmap('{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems), dtype='float', mode='r', shape=(self.cols, self.cols))
                    if self.do_LL:
                        self.LL_df = self.LL()
                    del self.coll_df
                    if self.do_LL_CS:
                        if not self.LL_df:
                            self.LL_df = np.memmap('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems), dtype='float', mode='r', shape=(self.cols, self.cols))
                        pipe = CatSimWin('LL', [self.w],
                                         lems=self.lems,
                                         CS_dir=self.orig,
                                         dest_dir='{}/Win_size_tests/LN'.format(self.orig),
                                         sim_algo='cosine',
                                         corpus=(self.orig.split('/')[-1], 1, 1.0, self.weighted),
                                         lem_file=self.lem_file)
                        self.CS('LL')
                        pipe.df = self.CS_df
                        del self.CS_df
                        del self.LL_df
                        pipe.ind = self.ind
                        pipe.SimCalc(self.w)
                        pipe.AveCalc(self.w)
                        pipe.WriteFiles()
                        self.param_dict['LL_window={}_lems={}_weighted={}'.format(self.w, self.lems, self.weighted)] = pipe.ave_no_93[self.w]
                        del pipe
                    self.coll_df = np.memmap('{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems), dtype='float', mode='r', shape=(self.cols, self.cols))
                    if self.do_PPMI:
                        self.PPMI_df = self.PPMI()
                    del self.coll_df
                    if self.do_PPMI_CS:
                        if not self.PPMI_df:
                            self.PPMI_df = np.memmap('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems), dtype='float', mode='r', shape=(self.cols, self.cols))
                        pipe = CatSimWin('PPMI', [self.w],
                                         lems=self.lems,
                                         CS_dir=self.orig,
                                         dest_dir='{}/Win_size_tests/LN'.format(self.orig),
                                         sim_algo='cosine',
                                         corpus=(self.orig.split('/')[-1], 1, 1.0, self.weighted),
                                         lem_file=self.lem_file)
                        self.CS('PPMI')
                        pipe.df = self.CS_df
                        del self.PPMI_df
                        del self.CS_df
                        pipe.ind = self.ind
                        pipe.SimCalc(self.w)
                        pipe.AveCalc(self.w)
                        pipe.WriteFiles()
                        self.param_dict['PPMI_window={}_lems={}_weighted={}'.format(self.w, self.lems, self.weighted)] = pipe.ave_no_93[self.w]
                        del pipe
                    if self.remove:
                        os.remove('{}/{}_{}_{}_coll_df.dat'.format(self.orig, self.w, self.weighted, self.lems))
                        os.remove('{}/{}_{}_{}_PPMI_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                        os.remove('{}/{}_{}_{}_LL_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                        os.remove('{}/{}_{}_{}_PPMI_CS_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                        os.remove('{}/{}_{}_{}_LL_CS_memmap.dat'.format(self.orig, self.w, self.weighted, self.lems))
                        os.remove('{}/{}_{}_{}_index.pickle'.format(self.orig, self.w, self.weighted, self.lems))
            print(self.param_dict)
        if self.do_LL_CS or self.do_PPMI_CS:
            dest_file = '{0}/Win_size_tests/{1}_{2}_{3}_weighted={4}_lems={5}_algos={6}.pickle'.format(
                self.orig, os.path.basename(self.orig), self.min_w, self.max_w, self.w_tests,
                self.l_tests, self.stat_algos)
            with open(dest_file, mode='wb') as f:
                dump(self.param_dict, f)
            with open(dest_file.replace('.pickle', '.csv'), mode='w') as f:
                f.write('Test Details\tMean Category Score\tCategory Z-Score')
                for k in sorted(self.param_dict.keys(),
                                key=lambda x: int(x.split('_')[1].split('=')[1])):
                    f.write('\n{}\t{}\t{}'.format(k, self.param_dict[k][0],
                                                  self.param_dict[k][1]))


def cmd():
    parser = argparse.ArgumentParser(description='Pipeline for automatic extraction of semantic data.')
    parser.add_argument('--win_size', type=int, default=10, help='The size of the contexts window')
    parser.add_argument('--lemmata', type=bool, default=False, help='Whether to use a lemmatized corpus or not')
    parser.add_argument('--weighted', type=bool, default=False, help='Whether to use a weighted or unweighted window. "True" == weighted')
    parser.add_argument('--algo', type=str, default='LL', choices=['LL', 'PPMI'], help='The significance algorithm to use')
    parser.add_argument('--files', type=str, help='The directory path in which the .txt files for your corpus are located.')
    parser.add_argument('--c', type=int, default=1, help='The number of cores to use during co-occurrence calculations')
    parser.add_argument('--occ_dict', type=str, help='The filepath to the file that contains the dictionary of word occurrences')
    parser.add_argument('--min_count', type=int, default=1, help='The minimum number of occurrences for words to be considered in the calculations')
    parser.add_argument('--jobs', type=int, default=1, help='The value for n_jobs in sklearn.metrics.pairwise_distances for cosine similarity calculations')
    parser.add_argument('--stops', type=bool, default=True, help='Whether to include stopwords in the calcuations')

    # Add subparsers for the whole process or for different steps
    subparsers = parser.add_subparsers(dest='subparser_name')
    parser_pipeline = subparsers.add_parser('SemPipeline')
    parser_pipeline.set_defaults(func=SemPipeline)
    parser_params = subparsers.add_parser('ParamTester')
    parser_params.add_argument('--min_w', type=int, help='The minimum context window size to be tested')
    parser_params.add_argument('--max_w', type=int, help='The maximum context window size to be tested')
    parser_params.add_argument('--step', type=int, help='The size of the steps to test between min_w and max_w')
    parser_params.add_argument('--w_tests', type=str, choices=['True', 'False', 'both'], help='Whether to test only the weighted window (True), the unweighted (False), or both (both)')
    parser_params.add_argument('--l_tests', type=str, choices=['True', 'False', 'both'], help='Whether to test only the lemmatized text (True), the unlemmatized text (False), or both (both)')
    parser_params.add_argument('--steps', type=str, default='all', choices=['all', 'coocs', 'LL', 'PPMI', 'LL_CS', 'PPMI_CS', 'remove'], help='The ParamTester functions to run')
    parser_params.set_defaults(func=ParamTester)
    args = parser.parse_args()
    if args.subparser_name == 'SemPipeline':
        args.func(**vars(args)).runPipeline()
    elif args.subparser_name == 'ParamTester':
        args.func(**vars(args)).RunTests()

if __name__ == '__main__':
    cmd()

'''if __name__ == '__main__':
    if sys.argv[1] == "SemPipeLine":
        SemPipeline(win_size=int(sys.argv[2]),
                    lemmata=bool(int(sys.argv[3])),
                    weighted=bool(int(sys.argv[4])),
                    algo=sys.argv[5],
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
'''