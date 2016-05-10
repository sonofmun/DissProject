Chapter 1 - Finding the Best Parameters for the Corpus
######################################################

The code for this chapter builds the foundation for the whole study in that it calculates the parameters that are used to produce the data for the rest of the dissertation. The central class in this chapter's code is the ParamTester class. First, the basic documentation for this class followed by a brief explanation of the input parameters.

The ParamTester Class
=====================

.. autoclass:: Data_Production.sem_extract_pipeline.ParamTester

As you can see, there are a lot of input parameters for this class. I will focus here on the less technical ones that are important for testing your corpus correctly. 

Formatting Your Corpus
----------------------

files (str)
^^^^^^^^^^^

At the same time the parameter that is the most important, easiest to understand, and requires the most explanation is the most explanation. ``files`` is a string that represents the directory path to the ``.txt`` files that make up your corpus, e.g., ``/home/matt/corpus``. I would recommend that your corpus be represented by one file for each work. Otherwise the co-occurrence context window (explained more below) will span from one work to another.

So far, so good. But the format of these files is also very important. The formatting is based on TEI markup, though the files need not be valid TEI to be used. Basically what this means is that ``ParamTester`` expects each individual word in each file to be on its own line and to be enclosed in a \<w\> tag. For example::

    <w>Βίβλος</w>
    <w>γενέσεως</w>
    <w>Ἰησοῦ</w>
    <w>χριστοῦ</w>
    <w>υἱοῦ</w>
    <w>Δαυὶδ</w>
    <w>υἱοῦ</w>
    <w>Ἀβραάμ</w>

If you plan on always using only the inflected words in your corpus, then this markup is enough. If, however, you want to be able to use lemmatized versions of the text, there is a special way to format each of these tags, once again in accordance with TEI markup principles without requiring complete TEI compliance. An example::

    <w lem="βίβλος">Βίβλος</w>
    <w lem="γένεσις">γενέσεως</w>
    <w lem="Ἰησοῦς">Ἰησοῦ</w>
    <w lem="Χριστός">χριστοῦ</w>
    <w lem="υἱός">υἱοῦ</w>
    <w lem="Δαυίδ">Δαυὶδ</w>
    <w lem="υἱός">υἱοῦ</w>
    <w lem="Ἀβραάμ">Ἀβραάμ</w>

The \@lem attribute on each \<w\> tag contains the word lemma information for each word. Note that having the value of each \@lem attribute surrounded by double quotes, i.e., ``"``, instead of single quotes, i.e., ``'`` is quite important if you want to be able to use this lemma information. If your texts are in this format, then you will be able to perform your calculations on either the lemmatized or the inflected text. 

l_tests (str)
^^^^^^^^^^^^^

The mention of lemmatized or inflected texts brings us to the next parameter, ``l_tests``. This is a string value representing whether the lemmas in the text should be used for calculation, the inflected words, or whether both tests should be run. A value of ``True`` will test only the lemmatized text, ``False`` will test only the inflected words, and ``both`` will run both tests.

The Parameters that ParamTester Tests
-------------------------------------

The following sections give a brief introduction of the parameters that ``ParamTester`` tests. For more information on these parameters, see the dissertation itself.

min_w (int), max_w (int), and step (int)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These three related parameters give the range for the context-window sizes that will be tested. ``min_w`` gives the minimum window size to be tested, ``max_w`` the maximum, and ``step`` the size of the step to be taken in between ``min_w`` and ``max_w``. So, for instance, if you wanted to test the window sizes 5, 10, 15, 20, 25, 30, you would set ``min_w=5``, ``max_w=30``, and ``step=5``.

w_tests (str)
^^^^^^^^^^^^^

``w_tests`` takes the same format and the same arguments as ``l_tests``, i.e., ``True``, ``False``, and ``both``. This parameter determines whether to use a weighted context window, an unweighted context window, or to test both types. An unweighted context window counts every word in the context window only one time, no matter its distance from the target word. A weighted context window, on the other hand, counts the words that are closer to the target word more times than the ones that are farther away. For instance, if you were using a 4-word context window, a weighted context window would count the words right before and after the target word 4 times, the words 2 words before and after 3 times, the words 3 words before and after 2 times, and the words 4 words away only once.

My own experience with Greek shows that for some corpora the weighted window is best, while for others the unweighted window is best. So I would certainly suggest testing both of these for all parameters.

stops (*(str)*)
^^^^^^^^^^^^^^^

``stops`` is a tuple that contains the words that you want to designate as stop words for your corpus. The default value is an empty tuple since my own tests with Greek have shown that results are improved by retaining the stop words during the calculations but then ignoring them, if desired, when interpreting the results. Only one set of stop words can be tested at a time. If you wish to test the results of several different stop word lists, you will need to designate and run tests on each of them individually.

sim_algo
^^^^^^^^

The only class instance variable that I will mention here is ``sim_algo``. ``ParamTester`` is not set up to take this as a parameter, instead defaulting to Cosine Similarity. If, however, you want to change the similarity algorithm used to compute the similarity of the distributional vectors, ``sim_algo`` accepts any *str* that is a valid ``metric`` for the ``sklearn.metrics.pairwise.pairwise_distances`` (`documentation <http://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.pairwise_distances.html#sklearn.metrics.pairwise.pairwise_distances>`_) function.

The CatSimWin Class
===================

.. autoclass:: Chapter_2.LouwNidaCatSim.CatSimWin

Test text.

Go To:

* :doc:`Index <index>`
* :doc:`Chapter 2 <chapter2>`
* :doc:`Chapter 3 <chapter3>`
* :doc:`Chapter 4 <chapter4>`
   
Return to the 