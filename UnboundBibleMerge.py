import re
from tkinter.filedialog import askopenfilename as askopen
from tkinter.filedialog import asksaveasfilename as asksave
Parsed = askopen(title = 'Where is your file containing the parsed Greek from Unbound Bible?')
Unparsed = askopen(title = 'Where is your file containing the unparsed Greek from Unbound Bible?')
with open(Parsed, encoding = 'utf-8') as PFile:
    parsedlist = PFile.readlines()
with open(Unparsed, encoding = 'utf-8') as UPFile:
    unparsedlist = UPFile.readlines()
pdict = {}
updict = {}
for pverse in parsedlist:
    if pverse.startswith('#') or pverse.startswith('\t'):
        continue
    else:
        repverse = re.search(r'\t\t([0-9]+)\t([^\n]+)', pverse) #I need to get this to match every line that I want
    try:
        pdict[repverse.group(1)] = repverse.group(2).split()
    except AttributeError as E:
        print(pverse)

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
