__author__ = 'matt'

import pandas as pd
import numpy as np

class WordtoCat:

    def __init__(self, word, cat, domains, data):
        """

        :return:
        """
        self.word = word
        self.cat = cat
        self.domains = pd.read_pickle(domains)
        self.data = pd.read_pickle(data)

    def compare(self):
        words = [list(x.items())[0] for x in self.domains[self.cat]['words']]
        self.df = pd.DataFrame(index=[x[0] for x in words], columns=['definition', 'CS_score', 'z-score'])
        self.df = self.df.drop_duplicates()
        mean = np.mean(self.data.values)
        std = np.std(self.data.values)
        for x in words:
            self.df.ix[x[0], 'definition'] = x[1]
            try:
                self.df.ix[x[0], 'CS_score'] = round(self.data.ix[x[0], self.word], 4)
                self.df.ix[x[0], 'z-score'] = round((self.df.ix[x[0], 'CS_score'] - mean)/std, 4)
            except KeyError:
                continue
        self.df = self.df.drop(self.word)
        self.df = self.df.sort_values(by="CS_score", ascending=False)
        print(self.df)
        print('CS:', np.mean(self.df.ix[:, 'CS_score']))
        print('Z-score:', np.mean(self.df.ix[:, 'z-score']))