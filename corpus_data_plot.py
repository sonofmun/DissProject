'''
The point of this script is to produce plots from the data in my biblical
corpora.
'''

import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilenames, askopenfilename
import os
import matplotlib.pyplot as plt

LN = pd.read_pickle(askopenfilename(title = 'Where is your LouwNida dictionary?'))
files = askopenfilenames(title = 'Which data files would you like to plot?')
corpora = {}
corp_names = {'LXX': 'Septuagint', 'PE': 'Pentateuch', 'FP': 'Former Prophets', 'LP': 'Later Prophets',
              'WR': 'Writings', 'IN': 'Intertestamental', 'GNT': 'New Testament'}

file_pattern = os.path.split(files[0])[1].split('_')
word = file_pattern[0]
for file in files:
    corpus = os.path.split(file)[1].split('_')[1]
    corpora[corp_names[corpus]] = pd.read_pickle(file)

highs = {}
#LXX_high = s_list[0][s_list[0]>100]
if 'LL' in file_pattern[-1]:
    measure = 'Log-likelihood'
    above = 20
    below = 10
    mult = 2
    for key in corpora.keys():
        highs[key] = corpora[key][corpora[key]>corpora[key].mean() + corpora[key].std()*mult]
elif 'CS' in file_pattern[-1]:
    measure = 'Cosine Similarity'
    above = .5
    below = .2
    mult = -2
    for key in corpora.keys():
        highs[key] = corpora[key][corpora[key]<corpora[key].mean() + corpora[key].std()*mult]

plt.figure(1)
plt.suptitle('%s Comparison of %s in the biblical corpora according to LouwNida semantic domains' % (measure, word), fontsize = 36)
counter = 0
for corpus in corpora.keys():
    plt.subplot(len(corpora),1,1+counter)
    plt.xlabel('LouwNida Semantic Domain')
    plt.ylabel('Average of %s scores' % measure)
    plt.plot(corpora[corpus])
    plt.title(corpus, fontsize = 24)
    plt.xlim(1,93)
    #plt.axhline(y = s_list[i].mean() + s_list[i].std(), c='r', ls='-')
    #plt.axhline(y = -(s_list[i].mean() + s_list[i].std()), c='r', ls='-')
    m = 0
    #for value in shared_high:
        #plt.axvline(x = value-1, color = 'red', label = str(value))
    for category, value in highs[corpus].iteritems():
        text_place = min(value*(1.5-(m%2)), corpora[corpus].max()*1.25)
        plt.annotate('%s =\n %s' % (LN[category]['Gloss'], round(value, 4)), xy = (category-1, value), xytext = (category-3, text_place), arrowprops=dict(facecolor='black', shrink=0.05, linewidth = .1), size = 18)
        m += 1
    plt.ylim(-corpora[corpus].std()*2, corpora[corpus].max()*1.5)
    counter += 1
plt.subplots_adjust(hspace = 0.4)
plt.show()
