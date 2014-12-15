'''
Coded by Matthew Munson
August 5, 2013
The purpose of this script is to scrape the information from
http://www.laparola.net/greco/louwnida.php and create a Python dictionary
for the information that can then be used to mark-up Greek vocabulary with
this information
'''
from bs4 import BeautifulSoup
import urllib.request
from pickle import dump
from collections import defaultdict
import sys
import re
from os.path import isfile

class extractLouwNida:

	def __init__(self, force = False):
		"""

		:param force: force recreation of local html files
		:type force: bool
		"""
		self.force = force
		self.url_base = 'http://www.laparola.net/greco/'
		self.save_dir = 'Data/Chapter_2/LN_html/'
		#LevelOne and LevelTwo will contain the first and second level URLs
		#LevelOne are the large categories (e.g., 'Geographical Objects and Features')
		#LevelTwo are the sub-categories (e.g., 'A Universe, Creation')
		self.LevelOne = []
		self.LevelTwo = []
		#L1Dict and L2Dict store the category descriptions at every level
		self.L1Dict = {}
		self.L2Dict = {}
		#WordDict is the final product that is then pickled and exported to txt
		self.WordDict = defaultdict(list)

	def download(self, url_ext):
		"""Download and save locally html from laparola.net

		:param url_ext: url extension
		:type url_ext: str or unicode
		"""
		cat = re.findall(r'sezmag=([0-9]{1,2})', url_ext)
		start = re.findall(r'sez1=([0-9]{1,3})', url_ext)
		end = re.findall(r'sez2=([0-9]{1,3})', url_ext)
		if end:
			filename = 'LN_{0}.{1}-{2}.html'.format(cat[0], start[0], end[0])
		elif cat:
			filename = 'LN_{0}.html'.format(cat[0])
		else:
			filename = 'LN_landing_page.html'
		if self.force or isfile(self.save_dir + filename) != True:
			print(filename)
			f = BeautifulSoup(urllib.request.urlopen(self.url_base + url_ext), 'html.parser')
			with open(self.save_dir + filename, mode='w', encoding='utf-8') as file:
				file.write(str(f))
			return f
		else:
			with open(self.save_dir + filename, mode='r', encoding='utf-8') as file:
				return BeautifulSoup(file.read(), 'html.parser')

	def buildDicts(self):
		#all links in the page lead to pages with more detailed category
		#information from the LN lexicon
		self.soup = self.download('louwnida.php')
		for link in self.soup.find_all('a'):
			try:
				#all LevelOne links can be automatically converted to int
				int(link.text)
				link_part = str(link.get('href'))
				self.LevelOne.append(link_part)
			except ValueError:
				#this captures LevelTwo links
				link_part = str(link.get('href'))
				if link_part != "None":
					self.LevelTwo.append(link_part)
			except TypeError:
				#this runs if there is no href attribute in link
				continue
		#the following is to add a link that should be in the page
		self.LevelTwo.append('louwnida.php?sezmag=68&sez1=34&sez2=57')

	def buildL1(self):
		#all h3 tags contain information about the large categories from LN
		for h3 in self.soup.find_all('h3'):
			L1List = list(h3.stripped_strings)
			self.L1Dict[L1List[0]] = {'gloss': L1List[1]}

	def buildL2(self):
		#all subcategory information is contained in <p> tags
		for paragraph in self.soup.find_all('p'):
			L2List = list(paragraph.stripped_strings)
			try:
				lims = L2List[1].split('-')
				if len(lims) == 2:
					cat = int(lims[0].split('.')[0])
					#the following is to correct a coding error on the page
					if cat > 93:
						cat = int(lims[1].split('.')[0])
					start = int(lims[0].split('.')[1])
					stop = int(lims[1].split('.')[1])
				elif len(lims) == 1:
					cat = int(lims[0].split('.')[0])
					start = int(lims[0].split('.')[1])
					stop = int(lims[0].split('.')[1])
			except IndexError:
				continue
			#The following is to correct an encoding error on the page
			if cat == 6 and start == 118:
				stop = 151
			self.L2Dict[(cat, start, stop)] = {'gloss': L2List[0].strip(' ('),
											   'words': []}
		#the following is to insert a link that should be in the page
		self.L2Dict[(68, 34, 57)] = {'gloss': '?', 'words': []}

	def buildWordDict(self):
		#acutes is because there seems to be a problem with acute accents
		#in the unicode of the LN online. This is for normalization to the
		#morphgnt standard.
		acutes = {'ά': 'ά', 'ό': 'ό', 'έ': 'έ', 'ώ': 'ώ', 'ί': 'ί', 'ή': 'ή', 'ύ': 'ύ',}
		for L1Link in self.LevelOne:
			L1Soup = self.download(L1Link)
			for GreekWords in L1Soup.find_all('tr'):
				if '<td>' in str(GreekWords):
					GreekWordsList = list(GreekWords.strings)
					if len(GreekWordsList) == 3:
						Word = GreekWordsList[0]
						for key in acutes.keys():
							Word = Word.replace(key, acutes[key])
						WordGloss = GreekWordsList[1]
						cat = int(GreekWordsList[2].split('.')[0])
						sect = int(GreekWordsList[2].split('.')[1])
						WordSection = tuple([cat, sect])
						#use .append because some sections have more than 1 word
						self.WordDict[WordSection].append({Word: WordGloss})
					elif len(GreekWordsList) == 5:
						Word = GreekWordsList[0]
						for key in acutes.keys():
							Word = Word.replace(key, acutes[key])
						WordGloss = GreekWordsList[3]
						cat = int(GreekWordsList[4].split('.')[0])
						sect = int(GreekWordsList[4].split('.')[1])
						WordSection = tuple([cat, sect])
						#use .append because some sections have more than 1 word
						self.WordDict[WordSection].append({Word: WordGloss.strip(') ')})
		for cat, start, stop in self.L2Dict.keys():
			for x in range(start, stop+1):
				if len(self.WordDict[(cat, x)]) != 0:
					for index, d in enumerate(self.WordDict[(cat, x)]):
						self.L2Dict[(cat, start, stop)]['words'].append(d)
		sys.setrecursionlimit(50000)
		dump(self.L2Dict, open('Data/Chapter_2/LN_Cat_Dict.pickle', mode='wb'))
		dump(self.WordDict, open('Data/Chapter_2/LN_Word_Dict.pickle', mode='wb'))