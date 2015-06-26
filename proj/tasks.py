from __future__ import absolute_import

import datetime
from celery import Celery
from collections import defaultdict, Counter
from scipy import linalg
import numpy as np

app = Celery()
app.config_from_object('celeryconfig')

__author__ = 'matt'

@app.task
def add(x, y):
	return x + y


@app.task
def mul(x, y):
	return x * y


@app.task
def xsum(numbers):
	return sum(numbers)

@app.task(name='proj.tasks.counter')
def counter(weighted, w, words, limits):
	b, e = limits
	cooc_dict = defaultdict(Counter)
	for i in range(b, e):
		t = words[i]
		c_list = []
		if weighted:
			for pos in range(max(i-w, 0),min(i+w+1, len(words))):
				if pos != i:
					for x in range(w+1-abs(i-pos)):
						c_list.append(words[pos])
		else:
			[c_list.append(c) for c in
			 words[max(i-w, 0):min(i+w+1, len(words))]]
			c_list.remove(t)
		cooc_dict[t] += Counter(c_list)
		#for c in c_list:
		#	try:
		#		cooc_dict[t][c] += 1
		#	except KeyError:
		#		cooc_dict[t][c] = 1
		if i % 100000 == 0:
			print('Processing token {0} of {1} for window size {2} at {3}'.format(i, len(words), w,
							datetime.datetime.now().time().isoformat()))
	return Counter(cooc_dict)

@app.task(name='proj.tasks.svd_calc')
def svd_calc(input, output, svd_exp, shape):
	svd_df = np.memmap(output, dtype='float', mode='w+', shape=shape)
	U, s, Vh = linalg.svd(input, check_finite=False)
	S = np.diag(s)
	svd_df[:] = np.dot(U, np.power(S, svd_exp))
	del svd_df