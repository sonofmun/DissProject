'''
The purpose of this script is to randomly choose cells in a DataFrame of
Fisher's exact values and to compare the value there with an independently
calculated value generated not using the Scipy.stats.fisher_exact function.
'''

import pandas as pd
import numpy as np
from tkinter.filedialog import askopenfilename
from math import factorial as m_f
import datetime


orig = askopenfilename(title = 'Which FE DF do you want to check?')
coll = askopenfilename(title = 'Where is the collocation file for this corpus?')

orig_df = pd.read_pickle(orig)
test_vals = pd.DataFrame(np.random.randint(0, len(orig_df)-1, size = (40,2)))
colls = pd.read_pickle(coll)

def fe_calc(a,b):
    c1 = np.sum(colls.ix[a])/8
    c12 = colls.ix[a, b]
    c2 = np.sum(colls.ix[:, b])/8
    w = c12
    x = max(c2-c12, 0)
    y = max(c1-c12, 0)
    z = N - c2 - c1 + c12
    p = (m_f(round(w+x))*m_f(round(y+z))*m_f(round(w+y))*m_f(round(x+z))/(fact_N*m_f(round(w))*m_f(round(x))*m_f(round(y))*m_f(round(z))))
    fe = orig_df.ix[a,b]
    return p, fe

comp_list = []
N = np.sum(colls.values)/8
fact_N = m_f(round(N))
my_counter = 0
for index, (a,b) in test_vals.iterrows():
    print('Now analyzing %s of %s rows at %s' % (index, len(test_vals), datetime.datetime.now().time().isoformat()))
    comp_list.append(fe_calc(a,b))
    my_counter += 1
    
