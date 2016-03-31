
'''
Created on 04. Dec. 2013
The purpose of this file is to take my pseudo-XML representations of the CCAT morphological files and convert the Greek words therein to unicode.
by Matthew Munson (mmunson@gcdh.de)
'''

import re
from tkinter.filedialog import askdirectory
from os import listdir
import os.path
#The following line is the mapping from the CCAT betacode characters to the appropriate unicode characters.
mapping = {'A': 'α', 'A(': 'ἁ', 'A(/': 'ἅ', 'A(/|': 'ᾅ', 'A(\\': 'ἃ', 'A(\\|': 'ᾃ', 'A(=': 'ἇ', 'A(=|': 'ᾇ', 'A(|': 'ᾁ', 'A)': 'ἀ', 'A)/': 'ἄ', 'A)/|': 'ᾄ', 'A)\\': 'ἂ', 'A)\\|': 'ᾂ', 'A)=': 'ἆ', 'A)=|': 'ᾆ', 'A)|': 'ᾀ', 'A/': 'ά', 'A/|': 'ᾴ', 'A=': 'ᾶ', 'A=|': 'ᾷ', 'A|': 'ᾳ', 'A\\': 'ὰ', 'E(': 'ἑ', 'E(/': 'ἕ', 'E(\\': 'ἓ', 'E)': 'ἐ', 'E)/': 'ἔ', 'E)\\': 'ἒ', 'E/': 'έ', 'E\\': 'ὲ', 'H(': 'ἡ', 'H(/': 'ἥ', 'H(/|': 'ᾕ', 'H(\\': 'ἣ', 'H(\\|': 'ᾓ', 'H(=': 'ἧ', 'H(=|': 'ᾗ', 'H(|': 'ᾑ', 'H)': 'ἠ', 'H)/': 'ἤ', 'H)/|': 'ᾔ', 'H)\\': 'ἢ', 'H)\\|': 'ᾒ', 'H)=': 'ἦ', 'H)=|': 'ᾖ', 'H)|': 'ᾐ', 'H/': 'ή', 'H/|': 'ῄ', 'H=': 'ῆ', 'H=|': 'ῇ', 'H|': 'ῃ', 'H\\': 'ὴ', 'I(': 'ἱ', 'I(/': 'ἵ', 'I(\\': 'ἳ', 'I(=': 'ἷ', 'I)': 'ἰ', 'I)/': 'ἴ', 'I)\\': 'ἲ', 'I)=': 'ἶ', 'I/': 'ί', 'I/+': 'ΐ', 'I\\+': 'ῒ', 'I+': 'ϊ', 'I=': 'ῖ', 'I=+\'': 'ῗ', 'I\\': 'ὶ', 'O(': 'ὁ', 'O(/': 'ὅ', 'O(\\': 'ὃ', 'O)': 'ὀ', 'O)/': 'ὄ', 'O)\\': 'ὂ', 'O/': 'ό', 'O\\': 'ὸ', 'R(': 'ῥ', 'R)': 'ῤ', 'U(': 'ὑ', 'U(/': 'ὕ', 'U(\\': 'ὓ', 'U(=': 'ὗ', 'U)': 'ὐ', 'U)/': 'ὔ', 'U)\\': 'ὒ', 'U)=': 'ὖ', 'U/': 'ύ', 'U/+': 'ΰ', 'U\\+': 'ῢ', 'U+': 'ϋ', 'U=': 'ῦ', 'U=+': 'ῧ', 'U\\': 'ὺ', 'W(': 'ὡ', 'W(/': 'ὥ', 'W(/|': 'ᾥ', 'W(\\': 'ὣ', 'W(\\|': 'ᾣ', 'W(=': 'ὧ', 'W(=|': 'ᾧ', 'W(|': 'ᾡ', 'W)': 'ὠ', 'W)/': 'ὤ', 'W)/|': 'ᾤ', 'W)\\': 'ὢ', 'W)\\|': 'ᾢ', 'W)=': 'ὦ', 'W)=|': 'ᾦ', 'W)|': 'ᾠ', 'W/': 'ώ', 'W=': 'ῶ', 'W=|': 'ῷ', 'W|': 'ῳ', 'W/|': 'ῴ', 'W\\': 'ὼ', '*A': 'Α', '*B': 'Β', 'B': 'β', '*G': 'Γ', 'G': 'γ', '*D': 'Δ', 'D': 'δ', '*E': 'Ε', 'E': 'ε', '*Z': 'Ζ', 'Z': 'ζ', '*H': 'Η', 'H': 'η', '*Q': 'Θ', 'Q': 'θ', '*I': 'Ι', 'I': 'ι', '*K': 'Κ', 'K': 'κ', '*L': 'Λ', 'L': 'λ', '*M': 'Μ', 'M': 'μ', '*N': 'Ν', 'N': 'ν', '*C': 'Ξ', 'C': 'ξ', '*O': 'Ο', 'O': 'ο', '*P': 'Π', 'P': 'π', '*R': 'Ρ', 'R': 'ρ', '*S': 'Σ', 'S': 'σ', 'J': 'ς', '*T': 'Τ', 'T': 'τ', '*U': 'Υ', 'U': 'υ', '*F': 'Φ', 'F': 'φ', '*X': 'Χ', 'X': 'χ', '*Y': 'Ψ', 'Y': 'ψ', '*W': 'Ω', 'W': 'ω', '*A(': 'Ἁ', '*A(/': 'Ἅ', '*A(/|': 'ᾍ', '*A(\\': 'Ἃ', '*A(\\|': 'ᾋ', '*A(=': 'Ἇ', '*A(=|': 'ᾏ', '*A(|': 'ᾉ', '*A)': 'Ἀ', '*A)/': 'Ἄ', '*A)/|': 'ᾌ', '*A)\\': 'Ἂ', '*A)\\|': 'ᾊ', '*A)=': 'Ἆ', '*A)=|': 'ᾎ', '*A)|': 'ᾈ', '*A/': 'Ά', '*A\\': 'Ὰ', '*E(': 'Ἑ', '*E(/': 'Ἕ', '*E(\\': 'Ἓ', '*E)': 'Ἐ', '*E)/': 'Ἔ', '*E)\\': 'Ἒ', '*E/': 'Έ', '*E\\': 'Ὲ', '*H(': 'Ἡ', '*H(/': 'Ἥ', '*H(/|': 'ᾝ', '*H(\\': 'Ἣ', '*H(\\|': 'ᾛ', '*H(=': 'Ἧ', '*H(=|': 'ᾟ', '*H(|': 'ᾙ', '*H)': 'Ἠ', '*H)/': 'Ἤ', '*H)/|': 'ᾜ', '*H': 'Η', '*H)\\|': 'ᾚ', '*H)=': 'Ἦ', '*H)=|': 'ᾞ', '*H)|': 'ᾘ', '*H/': 'Ή', '*H|': 'ῌ', '*H\\': 'Ὴ', '*I(': 'Ἱ', '*I(/': 'Ἵ', '*I(\\': 'Ἳ', '*I(=': 'Ἷ', '*I)': 'Ἰ', '*I)/': 'Ἴ', '*I)\\': 'Ἲ', '*I)=': 'Ἶ', '*I+': 'Ϊ', '*I/': 'Ί', '*I\\': 'Ὶ', '*O(': 'Ὁ', '*O(/': 'Ὅ', '*O(\\': 'Ὃ', '*O)': 'Ὀ', '*O)/': 'Ὄ', '*O)\\': 'Ὂ', '*O/': 'Ό', '*O\\': 'Ὸ', '*R(': '\u1FEC', '*U(': 'Ὑ', '*U(/': 'Ὕ', '*U(\\': 'Ὓ', '*U(=': 'Ὗ', '*U/': 'Ύ', '*U+': 'Ϋ', '*U\\': 'Ὺ', '*W(': 'Ὡ', '*W(/': 'Ὥ', '*W(/|': 'ᾭ', '*W(\\': 'Ὣ', '*W(\\|': 'ᾫ', '*W(=': 'Ὧ', '*W(=|': 'ᾯ', '*W(|': 'ᾩ', '*W)': 'Ὠ', '*W)/': 'Ὤ', '*W)/|': 'ᾬ', '*W)\\': 'Ὢ', '*W)\\|': 'ᾪ', '*W)=': 'Ὦ', '*W)=|': 'ᾮ', '*W)|': 'ᾨ', '*W|': 'ῼ', '*W/': 'Ώ', '*W\\': 'Ὼ', 'V': '\u03dd', '\#3': '\u03df', '\#5': '\u03e1', '\#': 'N'}
keyslist = list(mapping.keys()) # this produces a list of the keys from mapping that can then be ordered
keyslist.sort(key = len, reverse = True) #sorting by length is important so that a character is not converted to a less heavily polytonic character instead of the appropriately heavily polytonic one.
Orig = askdirectory(title = 'Where are your beta code XML files located?')
Dest = askdirectory(title = 'Where would you like to store your resulting UTF-8 XML files?')
OrigFiles = [x for x in listdir(Orig) if x.endswith('.txt') and re.match('[0-9]{2}', x)] #makes sure to select only the .txt files from the Orig folder and leaves out the file containing the whole LXX since this can be constructed from the parts
OrigFiles.sort()
with open(os.path.join(Dest, 'CCAT_UTF8.txt'), mode = 'w', encoding = 'utf-8') as LXXFile:
    for file in OrigFiles:
        destfile = ''.join([os.path.splitext(file)[0], '_UTF8', os.path.splitext(file)[1]])
        with open(os.path.join(Orig, file), encoding = 'utf-8') as origin:
            with open(os.path.join(Dest, destfile), mode = 'w', encoding = 'utf-8') as destination:
                for line in origin:
                    GreekWords = re.search(r'lem="([^"]+)">([^<]+)', line)
                    lem, word = GreekWords.group(1), GreekWords.group(2)
                    newlem, newword = lem, word
                    for key in keyslist:
                        GLetter = mapping[key]
                        newlem, newword = newlem.replace(key, GLetter), newword.replace(key, GLetter)
                    newline = line.replace(lem, newlem, 1)
                    newline = newline.replace(word, newword, 1)
                    destination.write(newline)
                    LXXFile.write(newline)