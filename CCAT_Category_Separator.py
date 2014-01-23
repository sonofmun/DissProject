import re
import os.path
books = {}
LXXParts = {'PE': [], 'FP': [], 'LP': [], 'WR': [], 'IN': []}
with open(r'C:\Users\matthew.munson\Documents\GitHub\DissProject\CCAT\CCAT_Book_Names.txt', encoding = 'utf-8') as BookFile:
    for name in BookFile:
        parts = re.match(r'(.+?):(.+?)\n', name)
        books[parts.group(1)] = parts.group(2)
with open(r'C:\Users\matthew.munson\Documents\GitHub\DissProject\CCAT\CCATUTF-8\CCAT_UTF8.txt', encoding = 'utf-8') as LXXFile:
    LXX = [x.rstrip('\n') for x in LXXFile]
for line in LXX:
    bookname = re.match(r'.+?\"(.+?)\..+', line).group(1)
    part = books[bookname]
    LXXParts[part].append(line)
for x in LXXParts:
    with open(os.path.join(r'C:\Users\matthew.munson\Documents\GitHub\DissProject\CCAT\CCATUTF-8', ''.join(['LXX_', x, '.txt'])), mode = 'w', encoding = 'utf-8') as PartFile:
        [PartFile.write(''.join([y, '\n'])) for y in LXXParts[x]]
