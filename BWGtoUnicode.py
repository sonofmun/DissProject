'''
Created on 22.08.2012

@author: matthew.munson
'''
def BWGtoUnicode(sourcepath, destpath):
    import re
    #The following line assigns the appropriate unicode characters to the existing BibleWorks beta code characters.
    #It will need to be changed if the source is something other than BibleWorks Greek.
    mapping = dict({'P': 'Π', 'a': 'α', 'b': 'β', 'R': 'Ρ', 'a`': 'ἁ', 'a[': 'ἅ', 'a[|': 'ᾅ', 'a|[': 'ᾅ', 'a]': 'ἃ', 'a]|': 'ᾃ', 'a-': 'ἇ', 'a-|': 'ᾇ', 'a`|': 'ᾁ', 'av': 'ἀ', 'a;': 'ἄ', 'a;|': 'ᾄ', 'a\'': 'ἂ', 'a\'|': 'ᾂ', 'a=': 'ἆ', 'a=|': 'ᾆ', 'av|': 'ᾀ', 'a,': 'ά', 'a,|': 'ᾴ', 'a/': 'ᾶ', 'a/|': 'ᾷ', 'a|': 'ᾳ', 'a.': '\u1F70', 'e`': 'ἑ', 'e[': 'ἕ', 'e]': 'ἓ', 'ev': 'ἐ', 'e;': 'ἔ', 'e\'': 'ἒ', 'e,': 'έ', 'e.': '\u1F72', 'h`': 'ἡ', 'h[': 'ἥ', 'h[|': 'ᾕ', 'h]': 'ἣ', 'h]|': 'ᾓ', 'h-': 'ἧ', 'h-|': 'ᾗ', 'h`|': 'ᾑ', 'hv': 'ἠ', 'h;': 'ἤ', 'h;|': 'ᾔ', 'h\'': 'ἢ', 'h\'|': 'ᾒ', 'h=': 'ἦ', 'h=|': 'ᾖ', 'hv|': 'ᾐ', 'h,': 'ή', 'h,|': 'ῄ', 'h/': 'ῆ', 'h/|': 'ῇ', 'h|': 'ῃ', 'h.': '\u1F74', 'i`': 'ἱ', 'i[': 'ἵ', 'i]': 'ἳ', 'i-': 'ἷ', 'iv': 'ἰ', 'i;': 'ἴ', 'i\'': 'ἲ', 'i=': 'ἶ', 'i,': 'ί', 'i<': 'ΐ', 'i>': 'ῒ', 'i?': 'ϊ', 'i/': 'ῖ', 'i\'': 'ῗ', 'i.': '\u1F76', 'o`': 'ὁ', 'o[': 'ὅ', 'o]': 'ὃ', 'ov': 'ὀ', 'o;': 'ὄ', 'o\'': 'ὂ', 'o,': 'ό', 'o.': '\u1F78', 'r`': 'ῥ', 'rv': 'ῤ', 'u`': 'ὑ', 'u[': 'ὕ', 'u]': 'ὓ', 'u-': 'ὗ', 'uv': 'ὐ', 'u;': 'ὔ', 'u\'': 'ὒ', 'u=': 'ὖ', 'u,': 'ύ', 'u<': 'ΰ', 'u>': 'ῢ', 'u?': 'ϋ', 'u/': 'ῦ', 'u\'': 'ῧ', 'u.': '\u1F7A', 'w`': 'ὡ', 'w[': 'ὥ', 'w[|': 'ᾥ', 'w]': 'ὣ', 'w]|': 'ᾣ', 'w-': 'ὧ', 'w-|': 'ᾧ', 'w`|': 'ᾡ', 'wv': 'ὠ', 'w;': 'ὤ', 'w;|': 'ᾤ', 'w\'': 'ὢ', 'w\'|': 'ᾢ', 'w=': 'ὦ', 'w=|': 'ᾦ', 'wv|': 'ᾠ', 'w,': 'ώ', 'w/': 'ῶ', 'w/|': 'ῷ', 'w|': 'ῳ', 'w,|': 'ῴ', 'w.': '\u1F7C', 'A': 'Α', 'a': 'α', 'B': 'Β', 'b': 'β', 'G': 'Γ', 'g': 'γ', 'D': 'Δ', 'd': 'δ', 'E': 'Ε', 'e': 'ε', 'Z': 'Ζ', 'z': 'ζ', 'H': 'Η', 'h': 'η', 'Q': 'Θ', 'q': 'θ', 'I': 'Ι', 'i': 'ι', 'K': 'Κ', 'k': 'κ', 'L': 'Λ', 'l': 'λ', 'M': 'Μ', 'm': 'μ', 'N': 'Ν', 'n': 'ν', 'X': 'Ξ', 'x': 'ξ', 'O': 'Ο', 'o': 'ο', 'P': 'Π', 'p': 'π', 'R': 'Ρ', 'r': 'ρ', 'S': 'Σ', 's': 'σ', 'j': 'ς', 'T': 'Τ', 't': 'τ', 'U': 'Υ', 'u': 'υ', 'F': 'Φ', 'f': 'φ', 'C': 'Χ', 'c': 'χ', 'Y': 'Ψ', 'y': 'ψ', 'W': 'Ω', 'w': 'ω', '~A': 'Ἁ', '{A': 'Ἅ', '{A|': 'ᾍ', '}A': 'Ἃ', '}A|': 'ᾋ', '_A': 'Ἇ', '_A|': 'ᾏ', '~A|': 'ᾉ', 'VA': 'Ἀ', ':A': 'Ἄ', ':A|': 'ᾌ', '"A': 'Ἂ', '"A|': 'ᾊ', '+A': 'Ἆ', '+A|': 'ᾎ', 'VA|': 'ᾈ', '<A': 'Ά', '~E': 'Ἑ', '{E': 'Ἕ', '}E': 'Ἓ', 'VE': 'Ἐ', ':E': 'Ἔ', '"E': 'Ἒ', '<E': 'Έ', '~H': 'Ἡ', '{H': 'Ἥ', '{H|': 'ᾝ', '}H': 'Ἣ', '}H|': 'ᾛ', '_H': 'Ἧ', '_H|': 'ᾟ', '~H|': 'ᾙ', 'VH': 'Ἠ', ':H': 'Ἤ', ':H|': 'ᾜ', 'H': 'Η', '"H|': 'ᾚ', '+H': 'Ἦ', '+H|': 'ᾞ', 'VH|': 'ᾘ', '<H': 'Ή', 'H|': 'ῌ', '~I': 'Ἱ', '{I': 'Ἵ', '}I': 'Ἳ', '_I': 'Ἷ', 'VI': 'Ἰ', ':I': 'Ἴ', '"I': 'Ἲ', '+I': 'Ἶ', 'I?': 'Ϊ', '~O': 'Ὁ', '{O': 'Ὅ', '}O': 'Ὃ', 'VO': 'Ὀ', ':O': 'Ὄ', '"O': 'Ὂ', '~R': '\u1FEC', '~U': 'Ὑ', '{U': 'Ὕ', '}U': 'Ὓ', '_U': 'Ὗ', 'VU': 'Ύ', '?U': 'Ϋ', '~W': 'Ὡ', '{W': 'Ὥ', '{W|': 'ᾭ', '}W': 'Ὣ', '}W|': 'ᾫ', '_W': 'Ὧ', '_W|': 'ᾯ', '~W|': 'ᾩ', 'VW': 'Ὠ', ':W': 'Ὤ', ':W|': 'ᾬ', '"W': 'Ὢ', '"W|': 'ᾪ', '+W': 'Ὦ', '+W|': 'ᾮ', 'VW|': 'ᾨ', 'W|': 'ῼ', 'V': '\u1FBD', 'Å': '.', '\\': '\u0387', '(': ',', ')': '.', 'È': ';', '&': '-', '^': '*', '%': ')', '$': '(', '#': ']', '@': '[', '!': '+', 'Î': '[', 'Ð': ']', '¹': '\"'})
    #The following two lines contain the paths for the source file (book) and the destination file (unibook).  Change them as necessary.
    book = open(sourcepath, 'r')
    unibook = open(destpath, 'w', encoding='utf-8')
    keys = mapping.keys()
    keys = list(keys)
    keys.sort(key = len, reverse = True)
    for line in book:
        #The following line extracts the book, chapter, and verse information.
        #It will only work for something set up like BibleWorks output that has a 3 letter book name, followed by a space, then the chapter number, a colon, then the verse number.
        #If the book, chapter, and verse information are in a different format, the regular expression will need to be changed.
        bookname = re.search(r'^[A-Za-z0-9]{3}', line)
        newline = ''
        pos = re.compile(r'@[a-z0-9]+')
        p = re.compile(r' +')
        tokenizedline = p.split(line)
        ampersand = '@'
        for word in tokenizedline:
            newword = word
            #The following "if" statement skips all POS analysis information.  This should not be converted to Greek characters.
            if ampersand not in word:
                #The following "if" statement skips the name of the biblical book.  This should not be converted to Greek characters.
                if word != bookname.group(0):
                    for key in keys:
                        GLetter = mapping[key]
                        newword = newword.replace(key, GLetter)
            if newline == '':
                newline = newword
            else:
                newline = newline + ' ' + newword
        unibook.write(newline)
    unibook.close()
    book.close()
