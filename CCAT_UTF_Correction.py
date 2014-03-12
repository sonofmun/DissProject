'''
The purpose of this file is to normalize and correct errors in the CCAT LXX lemmatization
files.  Normalization is primarily removing the hyphens and spaces between
prefixes and root words in verbs and then performing the necessary contractions
and phonetic transformations at the character level.  Normalization also includes
changing terminal sigmas to the terminal sigma form.  It also corrects some
obvious errors.  It takes as input the Prefix Transformation Dictionary.txt
file and a unicode rendering of the lemmata from CCAT and outputs a corrected
.txt file.
'''
import re
from tkinter.filedialog import askopenfilename, askdirectory
import os.path
UTFDir = askdirectory(title = 'Where are your CCAT XML Files located?')
TransFile = askopenfilename(title = 'Where is your Tranformation Dictionary File located?')
TransDict = {}
with open(TransFile, encoding = 'utf-8') as file:
    dictlist = file.readline().replace("'", '').split()
    for entry in dictlist:
        parts = entry.split(':')
        TransDict[parts[0]] = parts[1]
File_List = os.listdir(UTFDir)
for File in File_List:
    print(File)
    Cor_Lem_List = []
    Cor_Word_List = []
    split_path = os.path.splitext(File)
    CorrUTFFile = os.path.join(UTFDir, ''.join([split_path[0], '_Corrected', split_path[1]]))
    UTFFile = os.path.join(UTFDir, File)
    with open(UTFFile, encoding = 'utf-8') as file:
        filelist = [x.rstrip('\n') for x in file.readlines()] #reads all lines of the original file into a list, removing the carriage return in every line
    #lemmalist = [re.sub(r'.+?lem="([^"]*).*', r'\1', line) for line in filelist] #extracts a list of each word used in the text
    #wordlist = [re.sub(r'.+?>([^<]*).*', r'\1', line) for line in filelist]
    for i, line in enumerate(filelist):
        lem = re.sub(r'.+?lem="([^"]*).*', r'\1', line)
        lem2 = re.sub(r'[ -]', '', lem)
        lem3 = re.sub(r'σ\Z', 'ς', lem2)
        word = re.sub(r'.+?>([^<]*).*', r'\1', line)
        word2 = re.sub(r'σ\Z', 'ς', word)
        line2 = re.sub(word, word2, line)
        try:
            newline = line2.replace(lem, TransDict[lem2])#re.sub(lem, TransDict[lem], line2)
        except KeyError as E:
            newline = line2.replace(lem, lem3)
        filelist[i] = newline
    with open(CorrUTFFile, mode = 'w', encoding = 'utf-8') as file:
        for line in filelist:
            file.write(''.join([line, '\n']))
