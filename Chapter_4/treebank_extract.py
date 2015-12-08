__author__ = 'matt'

from lxml import etree

class extractDependencies:

	def __init__(self, target, orig, relation='sub', form='lemma'):
		self.target = target
		self.treebank = etree.parse(orig)
		self.relation = relation
		if form not in ['form', 'lemma']:
			print('Only "form" and "lemma" are valid values for form.')
		else:
			self.form = form

	def find_occs(self):
		self.occs = self.treebank.xpath('/proiel/source/div/sentence/token[@{0}="{1}"]'.format(self.form, self.target))

	def get_objects(self):
		self.dependents = []
		for occ in self.occs:
			h = occ.get('id')
			for s in self.treebank.xpath('//token[@head-id="{}"]'.format(h)):
				while s.get('empty-token-sort') and s.get('antecedent-id'):
					s = self.treebank.xpath('//token[@id="{}"]'.format(s.get('antecedent-id')))[0]
				try:
					if self.relation in s.get('relation'):
						if s.get('part-of-speech') == 'R-':
							p_obj = [x.get('form') for x in self.treebank.xpath('//token[@head-id="{}"]'.format(s.get('id')))]
							self.dependents.append([occ.get('citation-part'), occ.get('form'), '{} {}'.format(s.get('lemma'), ' '.join(p_obj)), s.get('part-of-speech'), s.get('citation-part')])
						else:
							self.dependents.append([occ.get('citation-part'), occ.get('form'), s.get('lemma'), s.get('part-of-speech'), s.get('citation-part')])
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