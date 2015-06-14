from unittest import TestCase
from proj.tasks import counter
from collections import Counter

__author__ = 'matt'


class TestCounter(TestCase):

	def test_repetition(self):
		t = 'the the the the the the the'.split()
		self.assertEqual(counter(True, 1, t, (0, len(t))), Counter({'the': Counter({'the': 12})}))

	def test_sentence(self):
		s = 'the quick brown fox jumped over the lazy green dog'.split()
		answer = Counter({'brown': Counter({'quick': 1, 'fox': 1}), 'green': Counter({'dog': 1, 'lazy': 1}), 'the': Counter({'quick': 1, 'over': 1, 'lazy': 1}), 'quick': Counter({'the': 1, 'brown': 1}), 'jumped': Counter({'over': 1, 'fox': 1}), 'over': Counter({'jumped': 1, 'the': 1}), 'dog': Counter({'green': 1}), 'lazy': Counter({'the': 1, 'green': 1}), 'fox': Counter({'jumped': 1, 'brown': 1})})
		self.assertEqual(counter(True, 1, s, (0, len(s))), answer)