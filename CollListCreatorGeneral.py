'''
Created on 18.01.2013

@author: matthew.munson
'''
import os.path
import pandas
from operator import itemgetter
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
LemListFile = askopenfilename(title = 'Where is the file that contains the ordered list of lemmas in your document?')
with open(LemListFile, mode = 'r', encoding = 'utf-8') as lemdoc:
    lemlist1 = lemdoc.readlines()
lemlist = [x.strip('\n') for x in lemlist1]
CollListDir = askdirectory(title = 'Where would you like to save all of your collocation lists?')
span = range(-10, 11) #set the span that you wish for the collocates
PosList = ['L10', 'L9', 'L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1', 'Lemma', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']
for lemma in lemlist: #iterates over every member of lemlist. returns en
    wordresults = []
    outputfile = os.path.join(CollListDir, "Coll_" + lemma + '.txt') #sets the output filename for the collocation list
    if os.path.isfile(outputfile) == True: #checks to see if a collocation file already exists for this lemma
        continue #if a collocation file for this lemma exists, it breaks out of the if loop and selects the next member of lemlist
    else: #this loop actually writes the collocation file
        output = open(outputfile, 'w', encoding = 'utf-8') #creates the appropriate output collocation file
        lastposition = 0
        wordpositions = []
        try:
            while lemlist.index(lemma, lastposition) is not ValueError: #finds en between lastposition and end of file
                #so this should be a list that goes from 0-the last position of en
                #and it should produce an error when it finds no more occurrences of en
                wordpositions.append(lemlist.index(lemma, lastposition)) #this appends the position of the current en to the list
                lastposition = lemlist.index(lemma, lastposition) +1 #this moves to the next position after the last occurrence so as not to keep counting the same occurrence.
        except ValueError as Error:
            for i in range(len(span)): #returns 0 as the first value
                colldict = {}
                collocatepositions = []
                collocates = []
                for position in range(len(wordpositions)):
                    collocatepositions.append(wordpositions[position] + span[i]) #span[0] is the first position listed in the span range, in this case -10.
                for collpos in collocatepositions:
                    if collpos >= 0 and collpos < len(lemlist):
                        collocates.append(lemlist[collpos])
                uniquecollocates = set(collocates)
                for collocate in uniquecollocates:
                    colldict[''.join(['P=', PosList[i], ' W=', collocate])] = collocates.count(collocate)
                orderedcolldict = sorted(colldict.items(), key = itemgetter(1), reverse = True) #colldict.items() returns a tuple of (key, value) pairs, key = itemgetter(1) orders the list based on index 1 of each pair, i.e., value.
                wordresults.append(orderedcolldict)
            wordresults = pandas.DataFrame(wordresults, index=['L10', 'L9', 'L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1', 'Lemma', 'R1', 'R2', 'R3', 'R4', 'R5', 
                                                               'R6', 'R7', 'R8', 'R9', 'R10'])
            wordresults = wordresults.transpose()
            wordresults.to_csv(output, encoding = 'utf-8', index = False)
            output.close()
