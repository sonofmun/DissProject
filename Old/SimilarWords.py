'''
Created on 07.02.2013

@author: matthew.munson
'''
import pickle
import nltk
lemdoc = open("C:/CompLing/GBible/XML/LemLists/GBibleLemmsNT.txt", mode = 'rb') #, encoding = 'utf-8')
lemlist = pickle.load(lemdoc)
lemstr = ''.join(lemlist)
lemstr.similar('Ἀβραάμ')
lemdoc.close()