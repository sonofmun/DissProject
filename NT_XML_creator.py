__author__ = 'matt'
"""This file takes the txt files from the SBLGNT Github repository, reformats
them in a simple xml-like format, and save them all into a single file.
"""

from os import listdir
import os.path
from tkinter.filedialog import askdirectory

orig = askdirectory(title='Where are your SBLGNT text files?')
dest = askdirectory(title='Where would you like to save your resulting'
                          'XML file?')

files = [x for x in listdir(orig) if x.endswith('.txt')]

for file in files:
    counter = 1
    old_id = ''
    with open(os.path.join(orig, file)) as f:
        lines = f.readlines()
    with open(os.path.join(dest, 'NT_text.txt'), mode='w') as f:
        for line in lines:
            l = line.split()
            if old_id != '.'.join([file.split('-')[1], l[0][2:4], l[0][4:]]):
                counter = 1
            id = '.'.join([file.split('-')[1], l[0][2:4].lstrip('0'),
                           l[0][4:].lstrip('0'), str(counter)])
            ana = '_'.join([l[1], l[2]])
            w = l[4]
            lem = l[-1]
            xml_line = ''.join(['<w ',
                                'id="', id,
                                '" ana="', ana,
                                '" lem="', lem,
                                '">', w, '</w>\n'])
            f.write(xml_line)
            old_id = '.'.join([file.split('-')[1], l[0][2:4], l[0][4:]])
            counter += 1