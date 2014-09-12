__author__ = 'matt'

import pandas as pd
from tkinter.filedialog import askopenfilenames
import os
import matplotlib.pyplot as plt
from collections import defaultdict
from math import ceil

files = askopenfilenames(title='Which data files would you like to plot?')
corpora = defaultdict(list)
corp_names = {'LXX': 'Septuagint',
              'PE': 'Pentateuch',
              'FP': 'Former Prophets',
              'LP': 'Later Prophets',
              'WR': 'Writings',
              'IN': 'Intertestamental',
              'GNT': 'New Testament'}

file_pattern = os.path.split(files[0])[1].split('_')
for file in files:
    corpus = os.path.split(file)[1].split('_')[1]
    corpora[corp_names[corpus]].append(pd.read_pickle(file))


def build_panels(d):
    """

    :param d:
    """
    for key in d.keys():
        if key[3] == 'weighted =True':
            weighted = 'Weighted'
        elif key[3] == 'weighted =False':
            weighted = 'Unweighted'
        pan.ix[key[0], key[1], weighted] = d[key]

    return pan

panels = {}
for corp in corpora.keys():
    panels[corp] = pd.Panel(items=['LL', 'LL_SVD', 'PLL', 'PPMI', 'PPMI_SVD'],
                  major_axis=list(range(1,81)),
                  minor_axis=('Weighted', 'Unweighted'))
    for each_dict in corpora[corp]:
        for key in each_dict.keys():
            if key[3] == 'weighted =True':
                weighted = 'Weighted'
            elif key[3] == 'weighted =False':
                weighted = 'Unweighted'
            panels[corp].ix[key[0], key[1], weighted] = each_dict[key]
            '''
            if key[3] == 'weighted =True':
                continue
            elif key[2] == 'lems=True':
                weighted = 'Weighted'
            elif key[2] == 'lems=False':
                weighted = 'Unweighted'
            panels[corp].ix[key[0], key[1], weighted] = each_dict[key]
            '''
plt.figure(1)
plt.suptitle('Parameter comparison for semantic information extraction',
             fontsize=36)
counter = 1
for corp in panels.keys():
    cols = 1 if len(panels) == 1 else 2
    plt.subplot(ceil(len(panels)/2),cols,counter)
    plt.ylabel('Perplexity Score')
    plt.xlabel('Window Size')
    ll_w, ll_uw = plt.plot(panels[corp]['LL'], color='k')
    #pll_w, pll_uw = plt.plot(panels[corp]['PLL'], color='k')
    pmi_w, pmi_uw = plt.plot(panels[corp]['PPMI'], color='k')
    ll_svd_w, ll_svd_uw = plt.plot(panels[corp]['LL_SVD'])
    plt.setp(ll_w, marker='o', markersize=8.0)
    plt.setp(ll_uw, marker='^', markersize=8.0)
    plt.setp(pmi_w, marker='s', markersize=8.0)
    plt.setp(pmi_uw, marker='*', markersize=8.0)
    #plt.setp(ll_svd_w, marker='x', markersize=8.0)
    #plt.setp(ll_svd_uw, marker='+', markersize=8.0)
    #plt.setp(pmi_svd_w, marker='x', markersize=8.0)
    #plt.setp(pmi_svd_uw, marker='+', markersize=8.0)
    plt.title(corp, fontsize = 24)
    plt.xticks([0, 9, 19, 29, 39, 49, 59, 69, 79],
               [1, 10, 20, 30, 40, 50, 60, 70, 80])
    counter += 1
    plt.legend([ll_w, ll_uw,  pmi_w, pmi_uw],
               ['LL Weighted', 'LL Unweighted',
                'PPMI Weighted', 'PPMI Unweighted'],
               loc=1)
    '''plt.legend([ll_w, ll_uw, ll_svd_w, ll_svd_uw,  pmi_w, pmi_uw],
               ['LL Weighted', 'LL Unweighted',
                'SVD Weighted', 'SVD Unweighted',
                'PPMI Weighted', 'PPMI Unweighted'],
               loc=1)
    '''
    '''plt.legend([ll_w, ll_uw, pmi_w, pmi_uw],
               ['LL Lemmatized', 'LL Unlemmatized',
               'PPMI Lemmatized', 'PPMI Unlemmatized'],
               loc=1)
    '''
plt.subplots_adjust(hspace = 0.4)
plt.show()