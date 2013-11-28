'''
Coded by Matthew Munson
August 5, 2013
The purpose of this script is to scrape the information from http://www.laparola.net/greco/louwnida.php and create a Python dictionary for the information that can then be used to mark-up Greek vocabulary with this information
'''
from bs4 import BeautifulSoup
import urllib.request
from html.parser import HTMLParser as Parse
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
'''for L1Link in LevelOne:
        L1Page = urllib.request.urlopen(L1Link)
        L1Text = handle_data(Parse, L1Link)'''
        
        
