Chapter 1 - Finding the Best Parameters for the Corpus
======================================================

The code for this chapter builds the foundation for the whole study in that it calculates the parameters that are used to produce the data for the rest of the dissertation. The central class in this chapter's code is the ParamTester class. First, the basic documentation for this class followed by a brief explanation of the input parameters.

The ParamTester Class
---------------------

.. autoclass:: Data_Production.sem_extract_pipeline.ParamTester

As you can see, there are a lot of input parameters for this class. I will focus here on the less technical ones that are important for testing your corpus correctly. 

Formatting Your Corpus
^^^^^^^^^^^^^^^^^^^^^^

files (str)
"""""""""""

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
"""""""""""""

The mention of lemmatized or inflected texts brings us to the next parameter, ``l_tests``. This is a string value representing whether the lemmas in the text should be used for calculation, the inflected words, or whether both tests should be run. A value of ``True`` will test only the lemmatized text, ``False`` will test only the inflected words, and ``both`` will run both tests.

The Parameters that ParamTester Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

