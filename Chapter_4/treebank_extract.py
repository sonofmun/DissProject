__author__ = 'matt'

from lxml import etree
from collections import defaultdict
import re


class extractDependencies:
    """Extracts specified syntactic relationships from PROIEL-formatted dependency treebank data.
    At this point, each specific relationship uses a different function, e.g., ``get_objects`` retrieves all of the
    tokens for which the target token is the head.

    :param target: The target word that is being analyzed.
    :type target: str
    :param orig: The full path to the XML file containing the treebank information
    :type orig: str
    :param relation: The code for the syntactic relationship that the target word should share with the other word (e.g., "sub")
    :type relation: str
    :param form: Whether to use the dictionary form of the target word ("lemma") or its inflected form ("form")
    :type form: str
    """
    
    def __init__(self, target, orig, relation='sub', form='lemma'):

        self.target = target
        self.treebank = etree.parse(orig).getroot()
        self.relation = relation
        if form not in ['form', 'lemma']:
            print('Only "form" and "lemma" are valid values for form.')
            self.form = 'lemma'
        else:
            self.form = form

    def find_occs(self):
        self.occs = self.treebank.xpath('/proiel/source/div/sentence/token[@{0}="{1}"]'.format(self.form, self.target))

    def get_objects(self):
        self.dependents = []
        for occ in self.occs:
            h = occ.get('id')
            for s in self.treebank.xpath('/proiel/source/div/sentence/token[@head-id="{}"]'.format(h)):
                #print(s.get('form'), s.get('relation'), s.get('citation-part'))
                while s.get('empty-token-sort') and s.get('antecedent-id'):
                    s = self.treebank.xpath('/proiel/source/div/sentence/token[@id="{}"]'.format(s.get('antecedent-id')))[0]
                try:
                    if self.relation in s.get('relation'):
                        if s.get('part-of-speech') == 'R-':
                            p_obj = [x.get('form') for x in self.treebank.xpath('/proiel/source/div/sentence/token[@head-id="{}"]'.format(s.get('id')))]
                            self.dependents.append([occ.get('citation-part'), occ.get('form'), '{} {}'.format(s.get('lemma'), ' '.join(p_obj)), s.get('part-of-speech'), s.get('citation-part')])
                        else:
                            self.dependents.append([occ.get('citation-part'), occ.get('form'), s.get('form'), s.get('part-of-speech'), s.get('citation-part')])
                except TypeError:
                    print(etree.tostring(s))
                    continue

    def get_subjects(self):
        self.dependents = []
        for occ in self.occs:
            h = occ.get('id')
            for s in self.treebank.xpath('//token[@head-id="{}"]'.format(h)):
                while s.get('empty-token-sort') and s.get('antecedent-id'):
                    s = self.treebank.xpath('//token[@id="{}"]'.format(s.get('antecedent-id')))[0]
                try:
                    if s.get('relation') == 'sub':
                        self.dependents.append([occ.get('citation-part'), occ.get('form'), s.get('lemma'), s.get('part-of-speech'), s.get('citation-part')])
                except TypeError:
                    print(etree.tostring(s))
                    continue

    def get_Christos(self):
        self.dependents = []
        for occ in self.occs:
            s = self.treebank.xpath('//token[@id="{}"]'.format(occ.get('head-id')))[0]
            while s.get('empty-token-sort') and s.get('antecedent-id'):
                s = self.treebank.xpath('//token[@id="{}"]'.format(s.get('antecedent-id')))[0]
            while s.get('lemma') == "Ἰησοῦς" or s.get('lemma') == 'κύριος':
                s = self.treebank.xpath('//token[@id="{}"]'.format(s.get('head-id')))[0]
            try:
                if 'N' in s.get('part-of-speech'):
                    self.dependents.append([occ.get('citation-part'), occ.get('form'), s.get('lemma'), s.get('part-of-speech'), s.get('citation-part')])
            except TypeError:
                print(etree.tostring(s))
                continue
        head_verses = defaultdict(list)
        for x in self.dependents:
            head_verses[x[2]].append(x[-1])
        with open('/media/matt/Data/DissProject/Data/Chapter_4/christou_head_words_verses.csv', mode='w') as f:
            f.write('Head word\tCount\tVerses\n')
            for h in sorted(head_verses.keys(), key=lambda x: len(head_verses[x]), reverse=True):
                f.write('{}\t{}\t{}\n'.format(h, len(head_verses[h]), head_verses[h]))

    def get_genitive_deps(self):
        self.dependents = []
        for occ in self.occs:
            h = occ.get('id')
            for s in self.treebank.xpath('//token[@head-id="{}"]'.format(h)):
                while s.get('empty-token-sort') and s.get('antecedent-id'):
                    s = self.treebank.xpath('//token[@id="{}"]'.format(s.get('antecedent-id')))[0]
                try:
                    if self.relation == s.get('relation') and re.match(r'.{6}g.{3}', s.get('morphology')) and s.get('part-of-speech') != 'S-':
                        self.dependents.append([occ.get('citation-part'), occ.get('form'), s.get('form'), s.get('part-of-speech'), s.get('citation-part')])
                except TypeError as E:
                    print(E, etree.tostring(s))
                    continue