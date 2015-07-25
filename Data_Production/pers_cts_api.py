__author__ = 'matt'

from lxml import etree
import re
from Data_Production.TK_files import tk_control
import requests

class GetGreekAuthor():

	def __init__(self, author=None, dest=None):
		'''

		:param author:
		:param work:
		:return:
		'''
		self.urn = 'urn:cts:greekLit:{0}'.format(author)
		self.dest = dest

	def getWorks(self):
		'''
		Gets urns for all the authors works in Perseus
		:return:
		'''
		request = 'http://services2.perseids.org/exist/rest/db/repository/CTS.xq?request=GetCapabilities&urn={0}&inv=annotsrc'.format(self.urn)
		root = etree.parse(request).getroot()
		self.works = {}
		for edition in root.xpath('//ti:edition', namespaces={'ti': 'http://chs.harvard.edu/xmlns/cts'}):
			#this will return only one URN per edition label
			#if several editions exist for the same work with the same edition
			#label, only the last one will be returned
			#This should, however, not be a problem since all editions should have
			#unique labels
			self.works[edition[0].text] = {'URN': edition.get('urn'), 'text': ''}

	def getText(self):
		'''
		Returns the text for every work returned by getWorks
		The texts are saved as lists of words in the "text" key in self.works
		They are also stripped of punctuation and lowercased.  If these elements
		are not desired, change punct to an empty string, delete the lower()
		method, or both.
		:return:
		'''
		punct = '\|·:᾿>\(;῾\]‘\?„\),’\-\[\*<“\'"”—\^⸨·#•\.'
		for edition in self.works.keys():
			request = 'http://services2.perseids.org/exist/rest/db/repository/CTS.xq?request=GetPassage&urn={0}&inv=annotsrc'.format(self.works[edition]['URN'])
			root = etree.parse(request).getroot()
			etree.strip_elements(root, 'milestone', with_tail=False)
			etree.strip_elements(root, 'bibl', with_tail=False)
			etree.strip_elements(root, 'head', with_tail=False)
			try:
				self.works[edition]['text'] = etree.tostring(root.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0], method='text', encoding=str)
			except IndexError:
				print(self.works[edition])
				continue
			#for paragraph in root.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			#	self.works[edition]['text'] = ' '.join([self.works[edition]['text'], etree.tostring(paragraph, method='text', encoding=str).strip()])
			self.works[edition]['text'] = re.sub(r'[{0}]'.format(punct), ' ', self.works[edition]['text']).lower().strip().split()

	def saveText(self):
		'''
		Saves the text as a txt file with one word per line and with each
		word surrounded by a <w> tag.
		:return:
		'''
		if self.dest:
			dest = self.dest
		else:
			dest = tk_control('askdirectory(title="In which directory would you like to save your files")')
		for edition in self.works.keys():
			with open('{0}/{1}_{2}.txt'.format(dest, ' '.join(edition.split()), self.works[edition]['URN']), mode='w', encoding='utf-8') as f:
				for word in self.works[edition]['text']:
					f.write('<w>{0}<\w>\n'.format(word))

	def pipeline(self):
		self.getWorks()
		self.getText()
		self.saveText()

class AuthorFromGit(GetGreekAuthor):

	def __init__(self, author=None, token=None, dest=None):
		'''

		:param author:
		:param work:
		:return:
		'''
		self.base = 'https://api.github.com/repos/PerseusDL/canonical-greekLit/contents/data/{0}'.format(author)
		self.auth = 'token {}'.format(token)
		self.dest = dest

	def getWorks(self):
		'''
		This goes through all subfolders in the canonical repository for the
		author and gets the URLs for all grc works by that author
		:return:
		'''
		#The ref param is to specify the branch to use
		works = requests.get(self.base, headers={'Authorization': self.auth})
		#Loop through each work level subdirectory for the author
		self.works = {}
		for work in works.json():
			#get the individual editions in the work
			try:
				editions = requests.get(work['url'], headers={'Authorization': self.auth})
			except TypeError:
				print(works.json())
				return
			for edition in editions.json():
				try:
					if 'grc' in edition['name'] and edition['name'].endswith('.xml'):
						self.works[edition['name']] = requests.get(edition['url'], headers={'Accept': 'application/vnd.github.VERSION.raw', 'Authorization': self.auth}).text
				except TypeError:
					continue

	def getText(self):
		'''
		Returns the text for every work returned by getWorks
		The texts are saved as lists of words in the "text" key in self.works
		They are also stripped of punctuation and lowercased.  If these elements
		are not desired, change punct to an empty string, delete the lower()
		method, or both.
		:return:
		'''
		punct = '\|·:᾿>\(;῾\]‘\?„\),’\-\[\*<“\'"”—\^⸨·#•\.'
		for edition in self.works.keys():
			try:
				root = etree.fromstring(self.works[edition].replace(' encoding="UTF-8"', ''))
			except etree.XMLSyntaxError:
				print(edition)
				continue
			etree.strip_elements(root, 'milestone', with_tail=False)
			etree.strip_elements(root, 'bibl', with_tail=False)
			etree.strip_elements(root, 'head', with_tail=False)
			etree.strip_elements(root, 'note', with_tail=False)
			try:
				text = etree.tostring(root.xpath('//body')[0], method='text', encoding=str)
			except IndexError:
				try:
					text = etree.tostring(root.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0], method='text', encoding=str)
				except IndexError:
					print('{0} has no //body'.format(edition))
					text = ''
			try:
				author = root.xpath('//author')[0].text
			except IndexError:
				try:
					author = etree.tostring(root.xpath('//tei:author', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0], method='text', encoding=str)
				except IndexError:
					print('{0} has no //author'.format(edition))
					author = ''
			try:
				work = root.xpath('//title')[0].text
				if work == 'Machine readable text':
					work = root.xpath('//title')[1].text
			except IndexError:
				try:
					work = etree.tostring(root.xpath('//tei:title', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0], method='text', encoding=str)
				except IndexError:
					print('{0} has no //title'.format(edition))
					work = ''
			self.works[edition] = {'text': text, 'author': author.strip(), 'work': work.strip()}
			#for paragraph in root.xpath('//tei:body', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
			#	self.works[edition]['text'] = ' '.join([self.works[edition]['text'], etree.tostring(paragraph, method='text', encoding=str).strip()])
			self.works[edition]['text'] = re.sub(r'[{0}]'.format(punct), ' ', self.works[edition]['text']).lower().strip().split()


	def saveText(self):
		'''
		Saves the text as a txt file with one word per line and with each
		word surrounded by a <w> tag.
		:return:
		'''
		if self.dest:
			dest = self.dest
		else:
			dest = tk_control('askdirectory(title="In which directory would you like to save your files")')
		for edition in self.works.keys():
			try:
				with open('{0}/{1}_{2}_{3}.txt'.format(dest, self.works[edition]['author'], self.works[edition]['work'], edition), mode='w', encoding='utf-8') as f:
					for word in self.works[edition]['text']:
						f.write('<w>{0}<\w>\n'.format(word))
			except TypeError:
				continue