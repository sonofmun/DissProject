import numpy as np
import pandas as pd
from decimal import *

def test_log():
    #P = min((C2/N)*8, 1) #N is the total number of words
    P = C2/N
    #values for p1
    P1 = C12/C1
    #values for p2
    P2 = (C2-C12)/(N-C1)
    LL1 = np.log(np.power(np.float128(P), (C12))*np.power(np.float128(1-P), (C1-C12)))
    print('LL1 for %s is %s' % (word, LL1))
    LL2 = np.log(np.power(np.float128(P), (C2-C12))*np.power(np.float128(1-P), ((N-C1)-(C2-C12))))
    print('LL2 for %s is %s' % (word, LL2))
    LL3 = np.log(np.power(np.float128(P1), (C12))*np.power(np.float128(1-P1), (C1-C12)))
    print('LL3 for %s is %s' % (word, LL3)) 
    LL4 = np.log(np.power(np.float128(P2), (C2-C12))*np.power(np.float128(1-P2), ((N-C1)-(C2-C12))))
    print('LL4 for %s is %s' % (word, LL4))
    LL = -2*(LL1+LL2-LL3-LL4)
    print('LL for %s is %s' % (word, LL))
    return LL

def test_fexact():
    from scipy.stats import fisher_exact
    f_e = fisher_exact([[C12, C2-C12],[C1-C12, N-C1-C2+C12]])
    print('Fisher of %s: %s' % (word, f_e))

words = ['καί', 'ἐν', 'ὁ', 'αὐτός', 'σύ', 'ἐγώ', 'εἶπον', 'κύριος', 'εἰς', 'υἱός', 'πρός', 'ἐπί', 'βασιλεύς', 'πᾶς', 'οὐ', 'Ἰσραήλ', 'εἰμί']
df = pd.read_pickle('/media/matt/DATA/Diss_Data/CCAT/CCAT_Coll/Binary/PE_binary_coll.pickle')
d = pd.read_pickle('/media/matt/DATA/Diss_Data/CCAT/CCAT_Coll/Coll_dicts/PE_coll_dict.pickle')
C1 = d['θεός']
N = sum(d.values())
for word in words:
    C2 = d[word]
    C12 = (df.ix['θεός', word])/8
    test_log()
    test_fexact()
