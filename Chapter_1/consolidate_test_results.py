__author__ = 'matt'

from glob import glob
import os
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from itertools import cycle


class win_tests:
    """ Collects and graphs the results of multiple runs of Data_Production.sem_extract_pipeline.ParamTester

    :param orig: the folder in which the .csv files containing the results are located
    :type orig: str
    :param corpus: the corpus that is being analyzed. This should be the same string used in the file names to designate the corpus (e.g., NT)
    :type corpus: str
    :param file_pattern: the file extension of the files containing the results
    :type file_pattern: str
    """

    def __init__(self, orig, corpus, file_pattern='*.csv'):
        self.files = glob('{}/{}{}'.format(orig, corpus, file_pattern))
        self.corpus = corpus
        self.orig = orig

    def build_df(self):
        d = defaultdict(dict)
        for x in sorted(self.files,
                        key=lambda x: int(os.path.basename(x).split('_')[1])):
            with open(x) as f:
                for line in sorted(f.read().split('\n')[1:]):
                    l = line.split('\t')[0].split('_')
                    w = int(l[1].split('=')[1])
                    c = '{}_{}_{}'.format(l[0], l[2], l[3])
                    d[c][w] = float(line.split('\t')[-1])
        self.df = pd.DataFrame(d)
        self.df.to_csv('{}/consolidated_{}.csv'.format(self.orig, self.corpus),
                       sep='\t')

    def graph_it(self):
        rotate = cycle([45, -45])
        offset = cycle([(0, 30), (0, -10)])
        marker = cycle(['k*-', 'k.-', 'kx-', 'ko-'])
        nolems_max_coords = [
            [self.df.ix[:, x].idxmax(), float(self.df.ix[:, x].max())] for x in
            self.df.columns if "lems=False" in x]
        lems_max_coords = [
            [self.df.ix[:, x].idxmax(), float(self.df.ix[:, x].max())] for x in
            self.df.columns if "lems=True" in x]
        [plt.plot(self.df.ix[:, x], marker.__next__(),
                  label=' '.join([x.split('_')[0], x.split('_')[2]])) for x in
         self.df.columns if "lems=False" in x]
        [plt.annotate(s=str(round(x[1], 4)), xy=x, xytext=offset.__next__(),
                      textcoords='offset points', rotation=rotate.__next__())
         for x in nolems_max_coords]
        plt.legend(loc=0, fontsize='small')
        plt.xticks(self.df.index)
        plt.xlim(self.df.index[0], self.df.index[-1])
        plt.xlabel('Window Size')
        plt.ylabel('Category Z-Score')
        plt.grid(True)
        #plt.tight_layout()
        plt.savefig('{}/nolem_graph.png'.format(self.orig), dpi=500)
        plt.clf()
        if lems_max_coords:
            [plt.plot(self.df.ix[:, x], marker.__next__(),
                      label=' '.join([x.split('_')[0], x.split('_')[2]])) for x
             in self.df.columns if "lems=True" in x]
            [plt.annotate(s=str(round(x[1], 4)), xy=x,
                          xytext=offset.__next__(), textcoords='offset points',
                          rotation=rotate.__next__()) for x in lems_max_coords]
            plt.legend(loc=0, fontsize='small')
            plt.xticks(self.df.index)
            plt.xlim(self.df.index[0], self.df.index[-1])
            plt.xlabel('Window Size')
            plt.ylabel('Category Z-Score')
            plt.grid(True)
            #plt.tight_layout()
            plt.savefig('{}/lem_graph.png'.format(self.orig), dpi=500)
            plt.clf()
