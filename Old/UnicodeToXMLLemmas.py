'''
Created on 22.08.2012

@author: matthew.munson
'''
def UnicodeToXML(sourcepath, destpath):
    import re
    # in the following two lines, you need to put the path for your input (unibook) and output (xmlbook) files.
    unibook = open(sourcepath, 'r', encoding='utf-8')
    xmlbook = open(destpath, 'w', encoding='utf-8')
    oldbookname = ''
    oldchapter = ''
    for line in unibook:
        wordnumber = 0
        #The following line extracts the book, chapter, and verse information.
        #It will only work for something set up like BibleWorks output that has a 3 letter book name, followed by a space, then the chapter number, a colon, then the verse number.
        #If the book, chapter, and verse information are in a different format, the regular expression will need to be changed.
        bookchapterverse = re.search(r'^([A-Za-z0-9]{3}) ([0-9]{1,4}:[0-9]{1,4})', line) #this line extracts the name of the biblical book from the beginning of the line that is being extracted
        bookname = bookchapterverse.group(1)
        chapterverse = bookchapterverse.group(2)
        newline = ''
        colonsplit = re.compile(r':')
        tokenizedline = line.split()
        ampersand = '@'
        endline = re.search(' $', line)
        if endline != None:
            line = line.strip(endline.group(0))
        for word in tokenizedline:
            newword = word
            if word != bookname:
                #the following if sequence extracts the chapter and verse and assigns them to separate variables.
                if word == chapterverse:
                    words = colonsplit.split(word)
                    chapter = words[0]
                    verse = words[1]
                    lastword = 'chapter'
                #the following elif runs for everything that is not POS information, or the book, chapter, and verse, which are dealt with above.
                elif ampersand not in word:
                    if lastword != '':
                        wordnumber += 1
                        wordnumberstring = bookname + '.' + chapterverse.replace(':', '.') + '.' + str(wordnumber)
                        openbracket = '<w id=\"' + wordnumberstring + '\"' 
                        wordtoken = word
                        lastword = ''
                    else:
                        wordtype = 'lem=\"' + word + '\">'
                #This assigns the POS analysis string to its own variable "ana"
                else:
                    analysis = 'ana=\"' + word.replace(ampersand, '') + '\"'
                    lastword = 'ana'
                #the following "if" runs after the word form, its lemma, and its analysis have been assigned to their appropriate variables.
                #it then builds the XML tag for each word token.
                if lastword == 'ana':
                    newword = openbracket + ' ' + analysis + ' ' + wordtype + wordtoken + '</w>\n'
                    xmlbook.write(newword)
        oldchapter = chapter
        oldbookname = bookname
    xmlbook.close()
    unibook.close()
