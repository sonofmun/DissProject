Chapter 4 - The Semantics of *pistis christou*
##############################################

Extracting Treebank Data
========================

.. autoclass:: Chapter_4.treebank_extract.extractDependencies

The only new task introduced in chapter 4 is the extraction of syntactic dependency data from dependency treebank data. The use of this code is fairly straightforward. The ``target`` parameter is simply the unicode string that represents the word whose sytnactic relationships are to be analyzed. The ``treebank`` parameter is the complete file path to the XML file in which the treebank data can be found. The ``relation`` parameter is the code used in the treebank data to represent syntactic relationship one hopes to find, e.g., "sub" for subject or "obl" for oblique. And, finally, the ``form`` parameter sets whether to search on the dictionary form of the word, in which case ``form="lemma"`` (the default) or the inflected form of the word, in case ``form="form"``. So, to find all of the occurrences of the word πίστις (*pistis*) in the New Testament in which πίστις has a genitive object, you would type in the following code::

    from Chapter_4.treebank_extract import extractDependencies
    pipe = extractDependencies(target="πίστις", orig="proiel-treebank/greek-nt.xml", relation="atr", form="lemma")
    pipe.get_genitive_deps()
    print(pipe.dependents[:10])

It should be pointed out that the code as it appears here depends on the PROIEL XML treebank format. I chose to follow the PROIEL format simply because treebank data for almost the entire New Testament is available in this format. However, the code is written in a way that should allow the user to replace any linguistic codes or XML attributes with those of their chosen treebank format.

Such analysis of syntactic relationships was an integral part of this chapter since much of the scholarly argumentation about the phrase *pistis christou* concerns the syntactic relationship of the two words within it and, more specifically, whether this relationship is a **subjective** genitive, i.e., that Christ is the one who believes, or an **objective** genitive, in which Christ is the one who is believed (in). The extraction of the location of all applicable phrases within (a part of) the New Testament was done using the ``get_genitive_deps`` function. But, unlike other syntactic analyses that have been published, I then used the semantic similarity of the noun *pistis* with its associated verb *pisteuo* (to believe, trust) to further delve into the meaning of "belief" in the Pauline epistles and in the New Testament in general by using the ``get_objects`` function to group the different types of objects with which *pisteuo* appears (e.g., accusative object, dative object/oblique, or with a prepositional object) to discover how each of these different object types is used by the New Testament authors. After painstaking interpretation of all of these different relationships, it became clear that belief for Paul consisted both in a belief in the story of Christ's resurrection and a trust that God would also resurrect those who were faithful to God as Christ had been. While this very brief summary cannot serve as evidence of the claims that I make, it does serve to show why I chose to bring syntactic data to bear in this chapter and how this syntactic data helped me to arrive at my conclusions.



Go to:

* :doc:`Index <index>`
* :doc:`Chapter 1 <chapter1>`
* :doc:`Chapter 2 <chapter2>`
* :doc:`Chapter 3 <chapter3>`