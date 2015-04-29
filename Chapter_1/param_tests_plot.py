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
    #sizes = list(range(20,31))
    sizes = list(range(1,501))
    #[sizes.append(x) for x in [40, 60, 100, 200, 300, 400, 500]]
    panels[corp] = pd.Panel(items=['LL', 'LL_LEM', 'PPMI', 'PPMI_LEM'],
                  major_axis=sizes,
                  minor_axis=('Weighted', 'Unweighted'))
    for each_dict in corpora[corp]:
        for key in each_dict.keys():
            if key[3] == 'weighted =True':
                weighted = 'Weighted'
            elif key[3] == 'weighted =False':
                weighted = 'Unweighted'
            if key[2] == 'lems=True':
                name = key[0] + '_LEM'
            else:
                name = key[0]
            panels[corp].ix[name, key[1], weighted] = each_dict[key]
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
ordered_corps = ['Septuagint',
                 'Pentateuch',
                 'Former Prophets',
                 'Later Prophets',
                 'Writings',
                 'Intertestamental',
                 'New Testament']
for corp in sorted(panels.keys(), key=lambda x: ordered_corps.index(x)):
    if len(panels) == 1:
        cols = 1
    elif len(panels) in [2, 4]:
        cols = 2
    else:
        cols = 3
    plt.subplot(ceil(len(panels)/3),cols,counter)
    plt.ylabel('Perplexity Score', fontsize=24)
    plt.xlabel('Window Size', fontsize=24)
    ll_w, ll_uw = plt.plot(panels[corp]['LL'], ls='')
    #pll_w, pll_uw = plt.plot(panels[corp]['PLL'])
    pmi_w, pmi_uw = plt.plot(panels[corp]['PPMI'], ls='')
    ll_lems_w, ll_lems_uw = plt.plot(panels[corp]['LL_LEM'], ls='')
    pmi_lems_w, pmi_lems_uw = plt.plot(panels[corp]['PPMI_LEM'], ls='')
    #plt.setp(ll_w, marker='o', markersize=12.0)
    #plt.setp(ll_uw, marker='^', markersize=12.0)
   # plt.setp(pmi_w, marker='s', markersize=12.0)
    #plt.setp(pmi_uw, marker='*', markersize=12.0)
    plt.setp(ll_lems_w, marker='D', markersize=12.0)
    plt.setp(ll_lems_uw, marker='d', markersize=12.0)
    plt.setp(pmi_lems_w, marker='x', markersize=12.0)
    plt.setp(pmi_lems_uw, marker='+', markersize=12.0)
    plt.title(corp, fontsize = 32)
    plt.xlim(0,501)
    plt.xticks([0, 19, 39, 59, 99, 199, 299, 399, 499],
               [1, 20, 40, 60, 100, 200, 300, 400, 500], fontsize=24)
    #plt.xticks(list(range(0,11)), list(range(20,32)), fontsize=24)
    plt.yticks(fontsize=24)
    counter += 1
    plt.legend([ll_lems_w, ll_lems_uw,  pmi_lems_w, pmi_lems_uw],
               ['LL Weighted', 'LL Unweighted',
                'PPMI Weighted', 'PPMI Unweighted'],
               loc=1)

    '''plt.legend([ll_w, ll_uw, ll_svd_w, ll_svd_uw,  pmi_w, pmi_uw],
               ['LL Weighted', 'LL Unweighted',
                'SVD Weighted', 'SVD Unweighted',
                'PPMI Weighted', 'PPMI Unweighted'],
               loc=1)
    '''
    '''plt.legend([ll_w, ll_uw,
                pmi_w, pmi_uw,
                ll_lems_w, ll_lems_uw,
                pmi_lems_w, pmi_lems_uw],
               ['LL Weighted Unlemmatized', 'LL Unweighted Unlemmatized',
               'PPMI Weighted Unlemmatized', 'PPMI Unweighted Unlemmatized',
               'LL Weighted Lemmatized', 'LL Unweighted Lemmatized',
               'PPMI Weighted Lemmatized', 'PPMI Unweighted Lemmatized'],
               loc=1)
    '''
plt.subplots_adjust(hspace=0.4)
plt.subplots_adjust(wspace=0.1)
plt.show()