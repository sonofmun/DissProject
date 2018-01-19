from unittest import TestCase
from Data_Production.sem_extract_pipeline import SemPipeline, ParamTester
from collections import Counter
import re
import os
import shutil
import numpy as np

__author__ = 'matt'


class TestInit(TestCase):
    def test_sim_algo_reset(self):
        """ Tests whether an incorrect value for sim_algo is changed to 'cosine'"""
        pipe = SemPipeline(sim_algo='default')
        self.assertEqual(pipe.sim_algo, 'cosine')

    def test_algo_reset(self):
        """ Tests whether an incorrect value for algo is changed to 'both'"""
        pipe = SemPipeline(algo='default')
        self.assertEqual(pipe.algo, 'both')


class TestUtils(TestCase):
    def setUp(self):
        os.mkdir('unit_tests/testing')
        self.pipe = SemPipeline(files='unit_tests/testing')
        self.pipe.dest = 'testing'
        self.pipe.corpus = 'TESTING'

    def tearDown(self):
        shutil.rmtree('unit_tests/testing')

    def test_produce_file_names(self):
        answer = 'testing/{step}_10_lems=True_TESTING_min_occ=1_no_stops=False_weighted=True.dat'
        self.assertEqual(self.pipe.produce_file_names('COOC'), answer.format(step='COOC'))

    def test_make_dest_new_directory(self):
        self.pipe.make_dest()
        self.assertTrue(os.path.isdir('unit_tests/testing/10'))

    def test_make_dest_existing_directory(self):
        os.mkdir('unit_tests/testing/10')
        self.pipe.make_dest()
        self.assertTrue(os.path.isdir('unit_tests/testing/10'))


class TestCounter(TestCase):
    def setUp(self):
        self.s = 'the quick brown fox jumped over the lazy green dog'.split()
        self.xml = ['<w id="Mt.1.1.1" ana="N-_----NSF-" lem="βίβλος">Βίβλος</w>',
                    '<w id="Mt.1.1.2" ana="N-_----GSF-" lem="γένεσις">γενέσεως</w>',
                    '<w id="Mt.1.1.3" ana="N-_----GSM-" lem="Ἰησοῦς">Ἰησοῦ</w>',
                    '<w id="Mt.1.1.4" ana="N-_----GSM-" lem="Χριστός">χριστοῦ</w>']
        self.inflected_pattern = re.compile(r'.+?>([^<]*).*')
        self.lem_pattern = re.compile(r'.+?lem="([^"]*).*')

    def test_sentence(self):
        """ Tests a sentence with a 1-word context window
        """
        answer = Counter({'brown': Counter({'quick': 1, 'fox': 1}), 'green': Counter({'dog': 1, 'lazy': 1}),
                          'the': Counter({'quick': 1, 'over': 1, 'lazy': 1}), 'quick': Counter({'the': 1, 'brown': 1}),
                          'jumped': Counter({'over': 1, 'fox': 1}), 'over': Counter({'jumped': 1, 'the': 1}),
                          'dog': Counter({'green': 1}), 'lazy': Counter({'the': 1, 'green': 1}),
                          'fox': Counter({'jumped': 1, 'brown': 1})})
        self.assertEqual(SemPipeline(win_size=1, c=1).word_counter(self.s, Counter()), answer)

    def test_unweighted_window(self):
        """ Tests a sentence with a 5 word, unweighted context window
        """
        counts = SemPipeline(win_size=5, weighted=False).word_counter(self.s, Counter())
        answer = Counter({'the': 2, 'quick': 1, 'brown': 1, 'fox': 1, 'over': 1, 'lazy': 1, 'green': 1, 'dog': 1})
        self.assertEqual(counts['jumped'], answer)

    def test_weighted_window(self):
        """ Tests a sentence with a 5 word, unweighted context window
        """
        counts = SemPipeline(win_size=5, weighted=True).word_counter(self.s, Counter())
        answer = Counter({'the': 6, 'quick': 3, 'brown': 4, 'fox': 5, 'over': 5, 'lazy': 3, 'green': 2, 'dog': 1})
        self.assertEqual(counts['jumped'], answer)

    def test_min_lems(self):
        """ Tests to make sure that words in the min_lems set are not counted
        """
        counts = SemPipeline(win_size=5, weighted=True).word_counter(self.s, Counter(), min_lems={'green'})
        answer = Counter({'the': 6, 'quick': 3, 'brown': 4, 'fox': 5, 'over': 5, 'lazy': 3, 'green': 2, 'dog': 1})
        self.assertEqual(counts['jumped'], answer)
        self.assertTrue('green' not in counts.keys())

    def test_inflected_word_extract(self):
        """ Tests to make sure that the inflected forms of words are extracted correctly from a string
        """
        words = SemPipeline().word_extract(self.xml, self.inflected_pattern)
        answer = ['Βίβλος', 'γενέσεως', 'Ἰησοῦ', 'χριστοῦ']
        self.assertCountEqual(words, answer)

    def test_lemmatized_word_extract(self):
        """ Tests to make sure that the lemmatized forms of words are extracted correctly from a string
        """
        words = SemPipeline().word_extract(self.xml, self.lem_pattern)
        answer = ['βίβλος', 'γένεσις', 'Ἰησοῦς', 'Χριστός']
        self.assertCountEqual(words, answer)


class TestAlgos(TestCase):
    def setUp(self):
        self.pipe = SemPipeline(files='unit_tests/data/temp_data')
        self.pipe.cols = 108
        self.pipe.coll_df = np.memmap(
            'unit_tests/data/10/COOC_10_lems=True_cooc_test_min_occ=1_no_stops=False_weighted=True.dat',
            dtype='float', mode='r', shape=(self.pipe.cols, self.pipe.cols)
        )
        self.ll_data = np.memmap(
            'unit_tests/data/10/LL_10_lems=True_cooc_test_min_occ=1_no_stops=False_weighted=True.dat',
            dtype='float', mode='r', shape=(self.pipe.cols, self.pipe.cols)
        )
        self.pipe.make_dest()

    def tearDown(self):
        shutil.rmtree(self.pipe.dest)
        del self.pipe

    def test_log_L(self):
        k = self.pipe.coll_df[0]
        n = np.sum(k)
        p = np.sum(self.pipe.coll_df, axis=0) / np.sum(self.pipe.coll_df)
        self.assertIsInstance(SemPipeline(algo='LL').log_L(k, n, p), np.memmap)
        self.assertEqual([x.round(7) for x in SemPipeline(algo='LL').log_L(k, n, p)[:5]],
                         [-2.0560897, -51.7183421, -49.3194270, -3.0913858, -1.0256429])

    def test_log_space_L(self):
        k = self.pipe.coll_df[0]
        n = np.sum(k)
        p = np.sum(self.pipe.coll_df, axis=0) / np.sum(self.pipe.coll_df)
        self.assertIsInstance(SemPipeline(algo='LL').log_space_L(k, n, p), np.memmap)
        self.assertEqual([x.round(7) for x in SemPipeline(algo='LL').log_space_L(k, n, p)[:5]],
                         [-2.0560897, -51.7183421, -49.3194270, -3.0913858, -1.0256429])

    def test_LL(self):
        self.pipe.LL()
        self.assertTrue(np.array_equal(np.round(self.pipe.LL_df, 7), np.round(self.ll_data, 7)))