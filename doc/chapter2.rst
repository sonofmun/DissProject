Chapter 2 - Comparison with Existing Semantic-Domain Lexica
###########################################################

There were no specific scripts written for Chapter 2, in which I compared the results of the distributional calculations described in this documentation to the semantic-domain categorization published in the Louw-Nida *Greek-English Lexicon of the New Testament Based on Semantic Domains*. Instead, after deciding which words I wanted to investigate (I chose words that had an abnormally low similarity to their primary semantic sub-domain), I simply extracted the top 100 most similar words using the following few lines typed into any Python interpreter::

    import numpy as np
    import pandas as pd
    i = pd.read_pickle('/PATH/TO/NT/DATA/NT/12/NT_IndexList_w=12_lems=True_min_occs=1_no_stops=False.pickle')
    d = np.memmap('/PATH/TO/NT/DATA/NT/12/LL_cosine_12_lems=True_NT_min_occ=1_SVD_exp=1.0_no_stops=False_weighted=False.dat', dtype='float', shape=(len(i), len(i)))
    s = pd.Series(d[i.index(WORD_UNDER_INVESTIGATION)], 
    

Go To:

* :doc:`Index <index>`
* :doc:`Chapter 1 <chapter1>`
* :doc:`Chapter 3 <chapter3>`
* :doc:`Chapter 4 <chapter4>`