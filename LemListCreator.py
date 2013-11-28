'''
Created on 23.01.2013

@author: matthew.munson
'''
import re
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
#import pickle
#Extract the lemmata into a list object
xmlfilename = askopenfilename(title = 'Where is your xml lemma file located?')
xmldoc = open(xmlfilename, 'r', encoding = 'utf-8') #opens the file for which you want a collocation list
lemfilename = asksaveasfilename(title = 'Where would you like to save your .txt lemma list?')
lemdoc = open(lemfilename, 'w', encoding = 'utf-8')
lemlist = [] #creates and empty list variable to hold the list of lemmata
for line in xmldoc: #this for loop removes the XML tagging and leaves a list variable containing one lemma in each position
    lemline = re.sub(r"<.+ lem=\"([-᾽\+\w]+)\">.+>\n", r"\1", line) #this line extracts the lemma from the XML
    if re.search(r'\s', lemline) is None: #this line ignores any line where the lemma was not extracted.  These are only lines with "[n]" where n is some number.  
        if re.search(r'\+', lemline) is not None: #This loop finds compound lemmata, e.g., kai+ego, and splits them into two lemmata
            lemline2 = re.split(r'\+', lemline) #splits the compound lemmata at the + sign
            lemlist.append(lemline2[0]) #adds the first element of the compound lemmata to the lemma list
            lemlist.append(lemline2[1]) #adds the second element of the compound lemmata to the lemma list
        else: #this portion of the loop executes for all lemmata that do not have a + in them
            lemlist.append(lemline)
lemliststr = str(lemlist)
lemliststr = lemliststr.strip('[]')
lemliststr = lemliststr.replace("', '", '\n')
lemdoc.write(lemliststr)
#pickle.dump(lemlist, lemdoc)
lemdoc.close()
xmldoc.close()