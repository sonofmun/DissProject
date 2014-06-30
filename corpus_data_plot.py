'''
The point of this script is to produce plots from the data in my biblical
corpora.
'''

import pandas as pd
from tkinter.filedialog import askdirectory, askopenfilename
import os
import matplotlib.pyplot as plt

orig = askdirectory(title = 'Where are your data files to be plotted?')
LN = pd.read_pickle(askopenfilename(title = 'Where is your Louw-Nida dictionary?'))
files = [x for x in os.listdir(orig) if x.endswith('.pickle')]
corpora = ['Pentateuch', 'Former Prophets', 'Later Prophets', 'Writings', 'Intertestamental Literature', 'New Testament']

file_pattern = files[0].split('_')
word = file_pattern[0]
#LXX = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'UTF8', file_pattern[-1]])))
PE = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'PE', file_pattern[-1]])))
FP = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'FP', file_pattern[-1]])))
LP = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'LP', file_pattern[-1]])))
WR = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'WR', file_pattern[-1]])))
IN = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'IN', file_pattern[-1]])))
NT = pd.read_pickle(os.path.join(orig, '_'.join([file_pattern[0], 'GNT', file_pattern[-1]])))
s_list = [PE, FP, LP, WR, IN, NT]
#LXX_high = s_list[0][s_list[0]>100]
if 'LL' in file_pattern[-1]:
    measure = 'Log-likelihood'
    above = 20
    below = 10
    mult = 2
    PE_high = s_list[0][s_list[0]>s_list[0].mean() + s_list[0].std()*mult]
    FP_high = s_list[1][s_list[1]>s_list[1].mean() + s_list[1].std()*mult]
    LP_high = s_list[2][s_list[2]>s_list[2].mean() + s_list[2].std()*mult]
    WR_high = s_list[3][s_list[3]>s_list[3].mean() + s_list[3].std()*mult]
    IN_high = s_list[4][s_list[4]>s_list[4].mean() + s_list[4].std()*mult]
    NT_high = s_list[5][s_list[5]>s_list[5].mean() + s_list[5].std()*mult]
elif 'CS' in file_pattern[-1]:
    measure = 'Cosine Similarity'
    above = 1
    below = 1
    mult = -2
    PE_high = s_list[0][s_list[0]<s_list[0].mean() + s_list[0].std()*mult]
    FP_high = s_list[1][s_list[1]<s_list[1].mean() + s_list[1].std()*mult]
    LP_high = s_list[2][s_list[2]<s_list[2].mean() + s_list[2].std()*mult]
    WR_high = s_list[3][s_list[3]<s_list[3].mean() + s_list[3].std()*mult]
    IN_high = s_list[4][s_list[4]<s_list[4].mean() + s_list[4].std()*mult]
    NT_high = s_list[5][s_list[5]<s_list[5].mean() + s_list[5].std()*mult]
shared_high = []
c_max = max(PE.max(), FP.max(), LP.max(), WR.max(), IN.max(), NT.max())+above
c_min = min(PE.min(), FP.min(), LP.min(), WR.min(), IN.min(), NT.min())-below
del PE, FP, LP, WR, IN, NT
all_highs = [PE_high, FP_high, LP_high, WR_high, IN_high, NT_high]
for cat in s_list[0].index:
    if cat in NT_high.index and cat in IN_high.index and cat in WR_high.index and cat in LP_high.index and cat in FP_high.index and cat in PE_high.index:
        shared_high.append(cat)
plt.figure(1)
plt.suptitle('%s Comparison of %s in the biblical corpora according to Louw-Nida semantic domains' % (measure, word), fontsize = 36)
for i, corpus in enumerate(s_list):
    plt.subplot(321+i)
    plt.xlabel('Louw-Nida Semantic Domain')
    plt.ylabel('Sum of %s scores' % measure)
    plt.plot(corpus)
    plt.title(corpora[i], fontsize = 24)
    plt.xlim(1,93)
    for value in shared_high:
        plt.axvline(x = value-1, color = 'red', label = str(value))
    for category, value in all_highs[i].iteritems():
        plt.annotate('%s =\n %s' % (LN[category]['Gloss'], round(value, 4)), xy = (category-1, value), xytext = (category-3, value*2), arrowprops=dict(facecolor='black', shrink=0.05, linewidth = .1))
    plt.ylim(c_min, c_max)
plt.subplots_adjust(hspace = 0.4)
plt.show()
