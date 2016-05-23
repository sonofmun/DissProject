__author__ = 'matt'

import numpy as np
import pandas as pd
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import scale
from itertools import combinations
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
import os


class comparison:

    """ Compares the vectors of a single word across the data from several different corpora.
    Note that the data from the different corpora must be normalized, preferably using sklearn.preprocessing.scale.

    :param base: the directory containing the sub-directories that contain the data for the different corpora
    :type base: str
    :param english: the english transcription of the word being analyzed (used only in file naming)
    :type english: str
    :param greek: the word in the alphabet of the target language. It must be written exactly as it is present in the corpora!
    :type greek: str
    :param measure: the type of data to use in the comparison, cosine similarity (CS), log-likelihood (LL), positive pointwise mutual information (PPMI), or raw co-occurrence counts (cooc)
    :type measure: str
    :param norm: whether the data needs to be normalized
    :type norm: bool

    :ivar corpora: the parameter information for each corpus to be used. Each corpus is represented by a tuple that contains the following information:
        **Corpus Name** *(str)*: should match the name of the parent folder in which the text files for the corpus are kept,
        **Best window size** *(str)*: the size of the context window as determined by ParamTester,
        **Minimum occurrences** *(int)*: the minimum number of times a word had to occur in your corpus before being used to produce data in SemPipeline,
        **Weighted or Unweighted window type** *(bool)*: whether the data for that corpus was produced using a weighted (True) or unweighted (False) context window type
    :type corpora: [(str, str, int, bool)]
    :ivar base: passed on from the ``base`` parameter
    :type base: str
    :ivar ekk_rows: an empty dictionary that will contain the vectors for each corpus
    :type ekk_rows: dict
    :ivar english: passed on from the ``english`` parameter
    :type english: str
    :ivar greek: passed on from the ``greek`` parameter
    :ivar prefix: part of the naming convention for the files from which the vectors will be extracted. Determined by the ``measure`` parameter
    :type prefix: str
    :ivar svd: part of the naming convention for the files from which the vectors will be extracted. Determined by the ``measure`` parameter
    :type svd: str
    :ivar norm: passed on from the ``norm`` parameter
    :type norm: bool
    """

    def __init__(self, base, english, greek, measure, norm=False, **kwargs):
        self.corpora = [('NT', '16', 1, True), ('LXX', '13', 1, True),
                        ('philo', '26', 1, False), ('josephus', '35', 1, False),
                        ('plutarch', '49', 1, False)]#, ('pers_data', '51', 1, False)]
        self.base = base
        self.ekk_rows = {}
        self.english = english
        self.greek = greek
        if measure == 'CS':
            self.prefix = 'LL_cosine'
            self.svd = ''
        elif measure == 'LL':
            self.prefix = 'LL'
            self.svd = ''
        elif measure == 'cooc':
            self.prefix = 'COOC'
            self.svd = ''
        elif measure == 'PPMI':
            self.prefix = 'PPMI'
            self.svd = ''
        else:
            print('"measure" must be "CS", "LL", "PPMI", or "cooc"')
        self.norm = norm

    def load_vectors(self):
        """ Loads the appropriate word vector from each corpus in self.corpora

        """
        for corp in self.corpora:
            rows = pd.read_pickle(
                '{0}{1}/{4}/{2}/{4}_IndexList_w={2}_lems=False_min_occs={3}_no_stops=False.pickle'.format(
                    self.base, corp[0], corp[1], corp[2], self.english))
            i = rows.index(self.greek)
            if self.norm:
                os.system('echo Now normalizing {}'.format(corp[0]))
                orig = np.memmap(
                    '{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False_weighted={7}.dat'.format(
                    self.base, corp[0], corp[1], corp[2], self.english, self.prefix, self.svd, corp[3]),
                    dtype='float', shape=(len(rows), len(rows)))
                normed = np.memmap(
                    '{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False_weighted={7}_NORMED.dat'.format(
                    self.base, corp[0], corp[1], corp[2], self.english, self.prefix, self.svd, corp[3]),
                    dtype='float', mode='w+', shape=(len(rows), len(rows)))
                normed[:] = scale(orig)
                r = normed[i]
                del normed
                del orig
            else:
                r = np.memmap(
                '{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False_weighted={7}_NORMED.dat'.format(
                    self.base, corp[0], corp[1], corp[2], self.english,
                    self.prefix, self.svd, corp[3]), dtype='float',
                shape=(len(rows), len(rows)))[i]
            self.ekk_rows[corp[0]] = pd.Series(r, index=rows)

    def sim_calc(self):
        """ Calculates the similarity for each vector with the others based on the words that the corpora share

        """
        self.cs_scores = pd.DataFrame(index=self.ekk_rows.keys(),
                                      columns=self.ekk_rows.keys())
        for combo in combinations(self.ekk_rows.keys(), 2):
            ekk_index = list(set(self.ekk_rows[combo[0]].index).intersection(
                set(self.ekk_rows[combo[1]].index)))
            self.cs_scores.ix[combo[0], combo[1]] = self.cs_scores.ix[
                combo[1], combo[0]] = (1 - pairwise_distances(
                self.ekk_rows[combo[0]][ekk_index],
                self.ekk_rows[combo[1]][ekk_index], metric='cosine'))[0][0]
            top_100 = abs(self.ekk_rows[combo[0]][self.ekk_rows[combo[0]] > 1] - self.ekk_rows[combo[1]][self.ekk_rows[combo[1]] > 1]).order().head(100)
            top_100.to_csv('{}/{}_{}_top_100_words.txt'.format(self.base, combo[0], combo[1]))
        self.cs_scores = self.cs_scores.fillna(1)

    def graph_it(self):
        """ Graphs the results on a bar graph

        """
        fig, ax = plt.subplots()

        index = np.arange(len(self.cs_scores))*1.2
        bar_width = 0.15

        opacity = 0.4
        #error_config = {'ecolor': '0.3'}
        mult = 0

        for corp in self.cs_scores:
            rects = plt.bar(index + bar_width * mult, self.cs_scores.ix[corp], bar_width, color='.9', label=corp)
            for i, rect in enumerate(rects):
                height = rect.get_height()
                if corp.islower():
                    name = corp.title()
                else:
                    name = corp
                ax.text(rect.get_x() + rect.get_width() / 2., height / 2, name, size='small', rotation='vertical', ha='center', va='bottom')
                if height != 1:
                    ax.text(rect.get_x() + rect.get_width() / 2., height + .01, round(height, 2), rotation='vertical', ha='center', va='bottom')
            mult += 1

        plt.xlabel('Corpus')
        plt.ylabel('CS Score')
        plt.title('CS comparison of word vectors')
        plt.xticks(index + 3 * bar_width, [x for x in self.cs_scores])
        plt.savefig('{}/{}_CS_corps_compare.png'.format(self.base, self.english), dpi=500)


class matrix_comparison(comparison):

    def load_vectors(self):
        for corp in self.corpora:
            self.ekk_rows[corp[0]] = pd.read_pickle(
                '{0}{1}/{4}/{2}/{4}_IndexList_w={2}_lems=False_min_occs={3}_no_stops=False.pickle'.format(
                    self.base, corp[0], corp[1], corp[2], self.english))

    def sim_calc(self):
        nt = self.corpora[0]
        self.scores = {}
        for corp in self.corpora:
            i_nt = []
            i_c2 = []
            rows = self.ekk_rows[corp[0]]
            for i, word in enumerate(self.ekk_rows['NT']):
                if word in rows:
                    i_nt.append(i)
                    i_c2.append(self.ekk_rows[corp[0]].index(word))
            d_c2 = np.memmap(
                '{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False_NORMED.dat'.format(
                    self.base, corp[0], corp[1], corp[2], self.english, self.prefix, self.svd),
                dtype='float32', shape=(len(rows), len(rows)))[i_c2]
            d_c2 = d_c2[:, i_c2]
            d_nt = np.memmap(
                '{0}{1}/{4}/{2}/{5}_{2}_lems=False_{4}_min_occ={3}_{6}no_stops=False_NORMED.dat'.format(
                    self.base, nt[0], nt[1], nt[2], self.english, self.prefix,
                    self.svd), dtype='float32',
                shape=(len(self.ekk_rows['NT']), len(self.ekk_rows['NT'])))[
                i_nt]
            d_nt = d_nt[:, i_nt]
            self.scores['{0}_{1}'.format('NT', corp[0])] = np.average(np.diag(
                1 - pairwise_distances(d_nt, d_c2, metric='cosine',
                                       n_jobs=12)))

def cmd():
    # base, english, greek, measure, norm=False
    parser = argparse.ArgumentParser(description='Compares distributional data across corpora.')
    parser.add_argument('--base', type=str, default='./', help='The file path for the parent folder in which all the corpora sub-folders are located')
    parser.add_argument('--english', type=str, help='The transliteration into Latin characters for the word under investigation')
    parser.add_argument('--greek', type=str, help='The word under investigation in its native alphabet')
    parser.add_argument('--measure', type=str, default='CS', choices=['CS', 'LL', 'PPMI', 'cooc'], help='The type of data to be used for the comparison')
    parser.add_argument('--norm', type=bool, default=False, help='Whether to run data normalization on the input matrices (should be True if the data has not yet been normalized')
    parser.set_defaults(func=comparison)
    args = parser.parse_args()
    pipe = args.func(**vars(args))
    pipe.load_vectors()
    pipe.sim_calc()
    pipe.graph_it()

if __name__ == '__main__':
    cmd()