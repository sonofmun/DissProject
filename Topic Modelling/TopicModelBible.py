import os
import numpy as np
import sklearn.feature_extraction.text as text
from sklearn import decomposition
from decimal import *
with open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\Greek Stop Words (Digital Classicist Wiki).txt', mode = 'r', encoding = 'utf-8') as StopFile:
    StopList = StopFile.read().split(', ')
paths = paths = [r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\UTF8\ChunkedNT']#, r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\UTF8\ChunkedLXX']
filenames = sorted([os.path.join(path, fn) for path in paths for fn in os.listdir(path) if fn.endswith('.txt')])
vectorizer = text.CountVectorizer(input='filename', stop_words = StopList, min_df=20)
dtm = vectorizer.fit_transform(filenames).toarray()
vocab = np.array(vectorizer.get_feature_names())
num_topics = 20
num_top_words = 20
clf = decomposition.NMF(n_components=num_topics, max_iter = 2000, random_state=1)
doc_topic = clf.fit_transform(dtm)
topic_words = []
for topic in clf.components_:
    word_idx = np.argsort(topic)[::-1][0:num_top_words]
    topic_words.append([[vocab[i], float(round(Decimal(topic[i]), 5))] for i in word_idx])
with open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\UTF8\NTTops.txt', mode = 'w+', encoding = 'utf-8') as TopicFile:
    for t in range(len(topic_words)):
        TopicFile.write("Topic {}: {}\n".format(t, ''.join(str(topic_words[t]).replace(r'[', '').replace(r']', ''))))

