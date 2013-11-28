'''
Created on 22.08.2012

@author: matthew.munson
'''
import re
import os
os.chdir('C:\CompLing\Jerome\Experiments\Zeta\EpistleVSHistorical\Corpus') #put the path to the destination files here
for files in os.listdir("."):
    filebase = files.rstrip('.txtTXT')
    destfiles = filebase + '_new.txt'
    destination = open(destfiles, 'w', encoding='utf-8') 
    if files.endswith(".txt") or files.endswith('.TXT'):
#        txtfiles.append(files)
#with fileinput.input(files=txtfiles) as source:
        with open(files, 'r'
           ) as source: #this should complete the line if the encoding is not utf-8
#            , encoding='utf-8') as source: #this should complete the line if the encoding is utf-8
            sourcetext = source.read()
            #the next line deletes any lines that begin with [nnn].  
            #I did this specifically for Jerome´s Epistula ad Damasum.  
            #It may not work for everything
#            if files in footnotefilelist:
#                footnotedel = re.compile(r'^[0-9]{1,3}.+?\n', re.S) 
            for line in sourcetext:
                bookchapterverse = re.compile(r'^([A-Za-z0-9]{3}) ([0-9]{1,4}:[0-9]{1,4})') #this line extracts the name of the biblical book from the beginning of the line that is being extractednotedel = re.compile(r'[\[\(\|].+?[\]\)\|]', re.S)
    #            titledel = re.compile(r'^EPISTOLA.+?\n', re.M)
    #            epistleintrodel = re.compile(r'^MONITUM.+?^EPISTOLA.+?\n', flags = re.S | re.M)
                newsource = bookchapterverse.sub('', line)
    #            newsource = notedel.sub('', newsource)
    #            newsource = epistleintrodel.sub('', newsource)
    #            newsource = titledel.sub('', newsource)
                destination.write(newsource)
    destination.close()
#unibook = open('C:/CompLing/GBible/GreekBibleUnicode.txt', 'r', encoding='utf-8')
#xmlbook = open('C:/CompLing/GBible/GreekBibleXML.txt', 'w', encoding='utf-8')
#oldbookname = ''
#oldchapter = ''
#for line in unibook:
#    wordnumber = 0
#    bookchapterverse = re.search(r'^([A-Za-z0-9]{3}) ([0-9]{1,4}:[0-9]{1,4})', line) #this line extracts the name of the biblical book from the beginning of the line that is being extracted
#    bookname = bookchapterverse.group(1)
#    chapterverse = bookchapterverse.group(2)
#    newline = ''
#    colonsplit = re.compile(r':')
#    tokenizedline = line.split()
#    ampersand = '@'
#    endline = re.search(' $', line)
#    if endline != None:
#        line = line.strip(endline.group(0))
#    for word in tokenizedline:
#        newword = word
#        if word == bookname:
#            if bookname != oldbookname:
#                if oldbookname != '':
#                    newword = '</chapter>\n</book>\n<book>' + newword + '\n'#+ '</book>'
#                    newline = newline + newword
#                elif oldbookname == '':
#                    newword = '<book>' + newword #+ '</book>'
#                    newline = newline + newword
#        elif word == chapterverse:
#            words = colonsplit.split(word)
#            chapter = words[0]
#            verse = words[1]
#            if chapter != oldchapter:
#                if oldchapter != '':
#                    newword = '<chapter>' + chapter + '\n<verse>' + verse #+ '</verse>'
#                    newline = newline + newword
#                elif oldchapter =='':
#                    newword = '<chapter>' + chapter + '\n' + '<verse>' + verse
#                    newline = newline + newword
#            else:
#                newword = '<verse>' + verse #+ '</verse>'
#                newline = newline + newword
#        elif ampersand not in word:
#            wordnumber = wordnumber + 1
#            wordnumberstring = bookname + '.' + chapterverse.replace(':', '.') + '.' + str(wordnumber)
#            newword = '<w id=\'' + wordnumberstring + '\'>' + word + '</w>'
#            newline = newline + newword
#        else:
#            newword = '<POS id=\'' + wordnumberstring + '\'>' + word.replace(ampersand, '') + '</POS>'
#            newline = newline + newword
##        newline = newline + newword
##    if oldchapter != chapter:
##        newline = newline + '</verse></chapter>\n'
##    else:
#    newline = newline + '</verse>\n'
#    xmlbook.write(newline)
#    oldchapter = chapter
#    oldbookname = bookname
#xmlbook.close()
#unibook.close()