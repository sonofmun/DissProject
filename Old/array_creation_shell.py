Python 3.3.2 (v3.3.2:d047928ae3f6, May 16 2013, 00:06:53) [MSC v.1600 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> import numpy as np
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('word1', '<f4'), ('word2', '<f4')]),('FP', [('word1', '<f4'), ('word2', '<f4')]),('LP', [('word1', '<f4'), ('word2', '<f4')])]
		)
>>> test
array([('', (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)),
       ('', (0.0, 0.0), (0.0, 0.0), (0.0, 0.0))], 
      dtype=[('Lemma', '<U30'), ('PE', [('word1', '<f4'), ('word2', '<f4')]), ('FP', [('word1', '<f4'), ('word2', '<f4')]), ('LP', [('word1', '<f4'), ('word2', '<f4')])])
>>> type(test[0][1}[0])
SyntaxError: invalid syntax
>>> type(test[0][1][0])
<class 'numpy.float32'>
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> type(test[0][1][0])
<class 'numpy.float64'>
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('word1', '<f16'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> type(test[0][1][0])
<class 'numpy.float32'>
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('word1', '<f64'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> type(test[0][1][0])
<class 'numpy.float32'>
>>> type(test[0]['PE']['word1'])
<class 'numpy.float32'>
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
Traceback (most recent call last):
  File "<pyshell#13>", line 1, in <module>
    test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
ValueError: mismatch in size of old and new data-descriptor
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('FP', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('LP', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')])])
Traceback (most recent call last):
  File "<pyshell#14>", line 1, in <module>
    test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('FP', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')]),('LP', [('Count', 'int')],[('word1', '<f8'), ('word2', '<f8')])])
ValueError: mismatch in size of old and new data-descriptor
>>> test = np.zeros((2,), [('Lemma', '<U30'),('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> test
array([('', (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)),
       ('', (0.0, 0.0), (0.0, 0.0), (0.0, 0.0))], 
      dtype=[('Lemma', '<U30'), ('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> test = np.zeros((2,), [('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])])
>>> test
array([ (((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))),
       (((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)))], 
      dtype=[('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])])])
>>> test = np.zeros([('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])])
Traceback (most recent call last):
  File "<pyshell#19>", line 1, in <module>
    test = np.zeros([('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])])
TypeError: an integer is required
>>> test = np.zeros((1,), [('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]),('FP', [('word1', '<f8'), ('word2', '<f8')]),('LP', [('word1', '<f8'), ('word2', '<f8')])])])
>>> test
array([ (((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)))], 
      dtype=[('Lemma1', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])]), ('Lemma2', [('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])])])
>>> test[0]
(((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)), ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0)))
>>> test[0]['Lemma1']['PE']
(0.0, 0.0)
>>> test['Lemma1']['PE']
array([(0.0, 0.0)], 
      dtype=[('word1', '<f8'), ('word2', '<f8')])
>>> test['Lemma1']
array([((0.0, 0.0), (0.0, 0.0), (0.0, 0.0))], 
      dtype=[('PE', [('word1', '<f8'), ('word2', '<f8')]), ('FP', [('word1', '<f8'), ('word2', '<f8')]), ('LP', [('word1', '<f8'), ('word2', '<f8')])])
>>> 
