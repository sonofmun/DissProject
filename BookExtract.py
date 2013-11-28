'''
Created on 21.08.2012

@author: matthew.munson
'''
import re #imports the regular expressions module
source = open('C:\CompLing\Jerome\From Hebrew\Corpus\He_gen - est.txt', 'r+') #opens the text from which we want to extract the information
oldbook = '' #initializes the variable 'oldbook'
target = '' #initializes the variable 'target'
for line in source: #this for loop loops over every line in the document and writes it to a new file
    book = re.search(r'^[A-Za-z0-9]{3}', line) #this line extracts the name of the biblical book from the beginning of the line that is being extracted
    file = 'C:/CompLing/Jerome/From Hebrew/Corpus/' + book.group(0) + '.txt' #this sets the name of the target file depending on what the name of the book is that was extracted from the beginning of 'line'
    if oldbook == '': #checks to see if this is the first line in the source file.  If it is, it assigns the value of book.group(0) to oldbook and then opens the target file.
        oldbook = book.group(0) #assigns the value of book.group(0) to oldbook
        target = open(file, 'w') #opens the target file for writing
    elif oldbook != book.group(0): #this loop runs when the program encounters a line in the source file from a new biblical book (i.e., it has a different book abbreviation at the beginning of the line)
        #print(book.group(0)) #checks the value of book.group(0).  Just for testing.
        #print(oldbook) #checks the value of oldbook.  Just for testing.
        target.close() #this closes the previous target file so that the lines from the new biblical book can be written to a new file.
        target = open(file, 'w') #this opens the new target file using the abbreviation of the biblical book as its name
        oldbook = book.group(0) #this assigns the value of book.group(0) to oldbook.  This makes it so that this if...elif loop does not run until the program encounters a line where the biblical book abbreviation is different at the beginning of the line.
    target.write(line) #this writes the contents of 'line' to the file just opened.  This is necessary within the loop so that if the next line within the source file starts a new book, the file for the previous book will be closed before trying to assign a new file name to 'target'
    #with open(file, 'a') as target: #this with loop automatically closes 'file' when the loop finishes.
        #target.write(line) #this writes the contents of 'line' to the file just opened.  This is necessary within the loop so that if the next line within the source file starts a new book, the file for the previous book will be closed before trying to assign a new file name to 'target'
target.close() #closes the last target file used
source.close() #closes the source file
input('Finished! Press return to continue.') #this is here to show the user when the program is finished.