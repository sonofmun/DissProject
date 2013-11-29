import re
from tkinter.filedialog import askopenfilename as askopen
from tkinter.filedialog import asksaveasfilename as asksave
Parsed = askopen(title = 'Where is your file containing the parsed Greek from Unbound Bible?')
Unparsed = askopen(title = 'Where is your file containing the unparsed Greek from Unbound Bible?')
Names = askopen(title = 'Where is the file with the book names mapped to the codes?')
namedict = {}
with open(Names, encoding = 'utf-8') as names:
    namelist = names.readlines()
for line in namelist:
    namedict[line.split('\t')[0]] = line.split('\t')[1]
Result = asksave(title = 'Where would you like to save your results?')
with open(Parsed, encoding = 'utf-8') as PFile:
    parsedlist = PFile.readlines()
with open(Unparsed, encoding = 'utf-8') as UPFile:
    unparsedlist = UPFile.readlines()
pdict = {}
updict = {}
for pverse in parsedlist:
    if pverse.endswith(' \n'):
        pverse += parsedlist.pop(parsedlist.index(pverse)+1) 
    if pverse.startswith('#') or pverse.startswith('\t'):
        continue
    else:
        repverse = re.search(r'([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]*)\t([0-9]+)\t([^\n]*)', pverse) #I need to get this to match every line that I want
    try:
        pdict[int(repverse.group(5))] = [repverse.group(1), repverse.group(2), repverse.group(3), repverse.group(4), repverse.group(6).split()]
    except AttributeError as E:
        print(pverse)
for npverse in unparsedlist:
    if npverse.endswith(' \n'):
        npverse += unparsedlist.pop(unparsedlist.index(npverse)+1) 
    if npverse.startswith('#') or npverse.startswith('\t'):
        continue
    else:
        renpverse = re.search(r'[^\t]+\t[^\t]+\t[^\t]+\t[^\t]*\t([0-9]+)\t([^\n]*)', npverse) #I need to get this to match every line that I want
    try:
        updict[int(renpverse.group(1))] = renpverse.group(2).split()
    except AttributeError as E:
        print(npverse)
with open(Result, mode = 'w', encoding = 'utf-8') as resfile:
    for x in sorted(pdict.keys()): #this will provide the key for every line in both dictionaries
        counter = 0
        for i, word in enumerate(pdict[x][4]): #this loop will go through every word in pdict[x] and match it with every word in updict[x]
            counter += 1
            wid = '.'.join([namedict[pdict[x][0]].rstrip('\n'), pdict[x][1], ''.join([pdict[x][2], pdict[x][3]]), str(counter)])
            lemana = word.split('-', maxsplit = 1)
            try:
                line = ''.join(['<w id="', wid, '" ana="', lemana[1], '" lem="', lemana[0], '">', updict[x][i], '</w>\n']) #I am getting an error here b/c they sometimes split the prefix from the word.  Need to deal with this.
            except IndexError as E:
                line = ''.join(['<w id="', wid, '" ana="None" lem="', lemana[0], '">', updict[x][i], '</w>\n'])
            resfile.write(line)
            

'''newparsedlist = parsedlist[:]
newunparsedlist = unparsedlist[:]
for pverse in parsedlist:
    if pverse.startswith('#') or pverse.startswith('\t'):
        newparsedlist.remove(pverse)
for npverse in unparsedlist:
    if npverse.startswith('#') or npverse.startswith('\t'):
        newunparsedlist.remove(npverse)
for pverse in newparsedlist:
    if pverse not in newunparsedlist:
        print(pverse)'''
