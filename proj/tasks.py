from __future__ import absolute_import

import datetime
import pandas as pd
from celery import Celery
from collections import defaultdict, Counter

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

	'''s = pd.Series(0, index=[t], name=t)
	if weighted:
		for pos in range(max(i-w, 0),min(i+w+1, len(words))):
			if pos != i:
				for x in range(w+1-abs(i-pos)):
					try:
						s[words[pos]] += 1
					except KeyError:
						s[words[pos]] = 1
	else:
		for pos in range(max(i-w, 0),min(i+w+1, len(words))):
			if pos != i:
				try:
					s[words[pos]] += 1
				except KeyError:
					s[words[pos]] = 1
	if i % 100000 == 0:
		print('Processing token %s of %s at %s' % (i, len(words),
						datetime.datetime.now().time().isoformat()))
	return s'''