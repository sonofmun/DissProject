'''
Coded by Matthew Munson
August 5, 2013
The purpose of this script is to scrape the information from http://www.laparola.net/greco/louwnida.php and create a Python dictionary for the information that can then be used to mark-up Greek vocabulary with this information
'''
from bs4 import BeautifulSoup
import urllib.request
from html.parser import HTMLParser as Parse
import re
import pickle

def handle_data(self, data):
        DataText = list(data)
        return DataText
Site = 'http://www.laparola.net/greco/louwnida.php'
f = urllib.request.urlopen(Site)
soup = BeautifulSoup(f, "html.parser")
LevelOne = []
LevelTwo = []
L1Dict = {}
L2Dict = {}
WordDict = {}
for link in soup.find_all('a'):
        if 'href' in str(link):
                if '&' not in str(link):
                        link_text = str(link.get('href'))
                        LevelOne.append('http://www.laparola.net/greco/' + link_text)
                else:
                        link_text = str(link.get('href'))
                        LevelTwo.append('http://www.laparola.net/greco/' + link_text)
for h3 in soup.find_all('h3'):
        L1List = handle_data(Parse, h3)
        for Data in L1List:
                if 'href' in str(Data):
                        L1Number = int(str(handle_data(Parse, Data)).strip("'[]'"))
                else:
                        L1Desc = Data.strip()
        L1Dict[L1Number] = L1Desc
for paragraph in soup.find_all('p'):
        L2List = handle_data(Parse, paragraph)
        if 'href' in str(L2List):
                for L2Data in L2List:
                        if 'href' in str(L2Data):
                                L2Number = str(handle_data(Parse, L2Data)).split(sep='.')[0].strip("[]'")
                        elif L2Data != ')' and L2Data != '),':
                                L2Letter = L2Data.split(maxsplit=1)[0]
                                L2Desc = L2Data.split(maxsplit=1)[1].strip(" ('[]")
                L2NumLet = L2Number+L2Letter
                L2Dict[L2NumLet] = L2Desc
for L1Link in LevelOne:
        L1Page = urllib.request.urlopen(L1Link)
        L1Soup = BeautifulSoup(L1Page)
        for GreekWords in L1Soup.find_all('tr'):
            if '<td>' in str(GreekWords):
                GreekWordsList = list(GreekWords.strings)
                if len(GreekWordsList) == 3:
                    Word = GreekWordsList[0]
                    WordGloss = GreekWordsList[1]
                    WordSection = GreekWordsList[2]
                    if WordDict.get(Word) != None:
                        WordDict[Word]['Section'].append({int(WordSection.split('.')[0]): [L1Dict[int(WordSection.split('.')[0]), int(WordSection.split('.')[1])})
                        WordDict[Word]['Gloss'].append({WordSection: WordGloss})
                        #= WordDict[Word] + [int(WordSection.split('.')[0]), L1Dict[int(WordSection.split('.')[0])], WordGloss, WordSection]
                    else:
                        #WordDict[Word] = [int(WordSection.split('.')[0]), L1Dict[int(WordSection.split('.')[0])], WordGloss, WordSection]
                        WordDict[Word]['Section'] = {int(WordSection.split('.')[0]): [L1Dict[int(WordSection.split('.')[0]), int(WordSection.split('.')[1])}
                        WordDict[Word]['Gloss'] = {WordSection: WordGloss}
for L2Link in LevelTwo:
        L2Page = urllib.request.urlopen(L2Link)
        L2Soup = BeautifulSoup(L2Page)
        SectionTitle = L2Soup.h4.string
        for GreekWords in L2Soup.find_all('tr'):
            if '<td>' in str(GreekWords):
                GreekWordsList = list(GreekWords.strings)
                if len(GreekWordsList) == 3:
                    Word = GreekWordsList[0]
                    WordGloss = GreekWordsList[1]
                    WordSection = GreekWordsList[2]
                    L2WordSection = WordSection.split('.')[0] + SectionTitle
                    WordDict[Word].insert(WordDict[Word].index(WordGloss), L2WordSection)
TextFile = open('/media/matt/DATA/Diss_Data/LouwNidaText.txt', mode='w', encoding='UTF-8')
DictFile = open('/media/matt/DATA/Diss_Data/LouwNidaDict.txt', mode='w', encoding='UTF-8')
#StrWordDict = str(WordDict)
#StrWordDict2 = re.sub(r"([\'\"]\],) ([\'\"])", r'\1\n\2', StrWordDict)
#DictFile.write(StrWordDict2)
pickle.dump(WordDict, DictFile)
DictFile.close()
StrWordDict = re.sub("[\'\"]\], [\'\"]", '\n', StrWordDict)
StrWordDict = re.sub("[\'\"]: \[", '\t', StrWordDict)
StrWordDict = re.sub("[\'\"], [\'\"]", '\t', StrWordDict)
StrWordDict = re.sub(", [\'\"]", '\t', StrWordDict)
StrWordDict = re.sub("[\'\"], [0-9]", '\t', StrWordDict)
StrWordDict = StrWordDict.strip("{}'")
TextFile.write(StrWordDict)
TextFile.close()
