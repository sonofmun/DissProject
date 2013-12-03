'''
Created 02. Dec. 2013

The purpose of this script is to pull all of the morphological files from CCAT and put them both into separate files for each .mlxx file on CCAT and into one big file representing the whole LXX.
The conversion of the CCAT Beta Code to unicode is taken care of by the CCATBetaUni.py file.

by Matthew Munson 
'''
from bs4 import BeautifulSoup as Soup
import urllib.request
from html.parser import HTMLParser as Parse
import re
import os.path
Site = 'http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/' #This is the current location of the CCAT morphological files.  If this location changes, obviously this will need to change as well.
f = urllib.request.urlopen(Site) #this line actually opens the HTML contents of the site into the variable f
soup = Soup(f, 'html.parser') #Beautiful Soup parses f using the html.parser from the Python html package
LXXList = [] #this list is populated with each line of the .mlxx files from the CCAT site
lastline = '' #this keeps track of the previous line.  This will be used to recognize the breaks between chapters in the .mlxx files.
with open(r'C:\Users\matthew.munson\Documents\GitHub\DissProject\CCATText\CCAT.txt', mode = 'w', encoding = 'utf-8') as CCATFile: #this is the file for the complete file of the whole LXX
    for link in soup.find_all(href=re.compile('mlxx')): #this loop opens every .mlxx file on the page, reads it into the BookPage variable, transforms it into a list of the lines, and then appends it to the LXXList variable, which collects the whole LXX.
        BookPage = urllib.request.urlopen(''.join([Site, link.get('href')])).read().decode(encoding = 'utf-8')
        SmallList = BookPage.split(sep = '\n')
        mlxx = str(link.get('href')) #this retrieves the name of the .mlxx file.  It will be used to name each of the resulting text files.
        print(mlxx) #this line is here to keep track of the progress of the program, i.e., to show which .mlxx file it is working on.
        with open(os.path.join(r'C:\Users\matthew.munson\Documents\GitHub\DissProject\CCATText', '.'.join([mlxx, 'txt'])), mode = 'w', encoding = 'utf-8') as MLXXFile:
            for line in SmallList: #this loop goes through every list in LXXList, each of which represents and .mlxx file from CCAT.
                if line == '':
                    lastline = line
                    continue
                elif lastline == '': #this basically collects the metadata that goes into the word id value.  It is not printed as such in the file so there is no need to .write to any file.
                    bcv = re.match(r'([A-Za-z0-9/]{,6}) ([0-9]{,4})\:{,1}([0-9]{,4})', line)
                    book = bcv.group(1) #book abbreviation
                    chapter = bcv.group(2) #chapter number
                    verse = bcv.group(3) #verse number
                    lastline = line
                    counter = 0
                else:
                    wal = re.match(r'([^ ]+) +([^ ]+) +([^ ]*) +([^ \n]+) *([^\n]*)', line)
                    word = wal.group(1) #this is the word as it appears in the text
                    ana1 = wal.group(2) #this is the first section of the CCAT morphological coding
                    ana2 = wal.group(3) #this is the second section of the CCAT morpohological coding
                    lemma = wal.group(4) #this is the lemma of the root word
                    pre = wal.group(5) #if the word is made up of a prefix and a root word, CCAT separates them.  This is the prefix
                    lastline = line
                    counter += 1
                    wordline = ''.join(['<w id="', '.'.join([book, chapter, verse, str(counter)]), '" ana="', ' '.join([ana1, ana2]).rstrip(' '), '" lem="', '-'.join([pre, lemma]).lstrip('-'), '">', word, '</w>\n']) #builds the XML-coded line
                    MLXXFile.write(wordline) #writes to the file for that individual .mlxx file
                    CCATFile.write(wordline) #writes to the file that contains the whole LXX
