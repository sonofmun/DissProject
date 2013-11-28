from bs4 import BeautifulSoup, element
import urllib.request
from operator import itemgetter
from string import punctuation
par_bible_file = open(r'C:\Users\mam3tc\Google Drive\Dissertation\CompLing\GBible\XML\ParallelBible\par_bible.txt', mode = 'w', encoding = 'utf-8')
abbs = {'Judges': 'Jdg', 'SongofSongs': 'Sol', 'Philemon': 'Phm'}
chapters = ['/interlinear/Genesis%201']
page_base = "http://studybible.info"
full_page = page_base + "/interlinear"
#site = urllib.request.urlopen(page)
#soup = BeautifulSoup(site, 'html.parser')
def chapterread(page):
    site = urllib.request.urlopen(page)
    soup = BeautifulSoup(site, 'html.parser')
    bookname = soup.find('h1').contents[0].rstrip('123456789 ').replace(' ', '')
    if bookname in abbs:
        bookname = abbs[bookname]
    else:
        bookname = ''.join(bookname[:3])
    greekkey = ''
    engcontents = []
    greekvalue = ''
    greekdict = {}
    for units in soup.find_all(class_ = 'unit'):
        if units.find(class_ = 'ref greek'):
            wordcount = 0
            chapterverse = str(units.find(class_ = 'ref greek').contents).strip("[]'").replace(':', '.')
            chap_vers_split = chapterverse.split('.')
            if chap_vers_split[1].isalpha():
                chap_vers_split[1] = 0
                chapterverse = '.'.join([str(chap_vers_split[0]), str(chap_vers_split[1])])
        else:
            engcontents = units.find(class_ = 'english').contents
            for i, item in enumerate(engcontents):
                if isinstance(item, element.Tag):
                    engcontents[i] = ''
            greekvalue = ''.join(engcontents).strip().lower()
            greekkey = ''.join(units.find(class_ = 'greek').contents).lower()
            if ' ' in greekkey:
                greekkey = greekkey.split()
                greekvalue = greekvalue.upper()
                for key in greekkey:
                    wordcount += 1
                    chapterverseword = '.'.join([bookname, chapterverse, str(wordcount)])
                    greekdict[chapterverseword] = {key: greekvalue}
            else:
                wordcount += 1
                chapterverseword = '.'.join([bookname, chapterverse, str(wordcount)])
                greekdict[chapterverseword] = {greekkey: greekvalue}
    return greekdict, soup
def write_to_file(x):
    x_keys = list(iter(x))
    for i, item in enumerate(x_keys):
        split_item = item.split('.')
        split_item = [int(s) if s.isdigit() else s for s in split_item]
        '''for sub_i, sub_item in enumerate(split_item):
            if sub_i > 0:
                split_item[sub_i] = int(sub_item)'''
        x_keys[i] = split_item
    tertiary_sort = sorted(x_keys, key = itemgetter(3))
    try:
        primary_sort = sorted(tertiary_sort, key = itemgetter(2))
    except TypeError:
        for tert_item in tertiary_sort:
            if isinstance(tert_item[2], str):
                tert_item[2] = 0
        #secondary_sort = [tert_item[2] = 0 if isinstance(tert_item[2], str) for tert_item in tertiary_sort]
        primary_sort = sorted(tertiary_sort, key = itemgetter(2))
    #primary_sort = [str(s) for s in x for x in secondary_sort]
    #primary_sort = sorted(itemgetter(2)(secondary_sort), key = str.isdigit)
    for key in primary_sort:
        joined_key = '.'.join([key[0], str(key[1]), str(key[2]), str(key[3])])
        par_bible_file.write(''.join(['<w id="', joined_key, '" eng="', str(x[joined_key]).split(':')[1].strip("}' ").strip(punctuation), '">', str(x[joined_key]).split(':')[0].strip("{' "), '</w>', '\n']))
dict_to_write, the_soup = chapterread(full_page)
write_to_file(dict_to_write)
while the_soup.find(class_='next_chapter')['href'] not in chapters:
    full_page = ''.join([page_base, the_soup.find(class_='next_chapter')['href']])
    chapters.append(the_soup.find(class_='next_chapter')['href'])
    dict_to_write, the_soup = chapterread(full_page)
    write_to_file(dict_to_write)
    print(full_page)
par_bible_file.close()
'''page = "http://studybible.info/interlinear"
    site = urllib.request.urlopen(page)
    soup = BeautifulSoup(site, 'html.parser')
    bookname = soup.find('h1').contents[0].rstrip('123456789 ').replace(' ', '')
    if bookname in abbs:
        bookname = abbs[bookname]
    else:
        bookname = ''.join(bookname[:3])
    greekkey = ''
    engcontents = []
    greekvalue = ''
    greekdict = {}
    for units in soup.find_all(class_ = 'unit'):
        if units.find(class_ = 'ref greek'):
            wordcount = 0
            chapterverse = str(units.find(class_ = 'ref greek').contents).strip("[]'").replace(':', '.')
        else:
            engcontents = units.find(class_ = 'english').contents
            for i, item in enumerate(engcontents):
                if isinstance(item, element.Tag):
                    engcontents[i] = ''
            greekvalue = ''.join(engcontents).strip().lower()
            greekkey = ''.join(units.find(class_ = 'greek').contents).lower()
            if ' ' in greekkey:
                greekkey = greekkey.split()
                for key in greekkey:
                    wordcount += 1
                    chapterverseword = '.'.join([bookname, chapterverse, str(wordcount)])
                    greekdict[chapterverseword] = {key: greekvalue}
            else:
                wordcount += 1
                chapterverseword = '.'.join([bookname, chapterverse, str(wordcount)])
                greekdict[chapterverseword] = {greekkey: greekvalue}
        
        print(greek)
        if greek.get('class')[0] == 'greek':
            for i, item in enumerate(greek.contents):
                greek.contents[i] = str(greek.contents[i])
                greekkey = ''.join(greek.contents).lower()
        elif greekkey != '' and greek.get('class')[0] == 'english':
            for i in range(len(greek.contents)):
                if isinstance(greek.contents[i], bs4.contents.Tag):
                    del greek.contents[i]
                else:
                    greek.contents[i] = str(greek.contents[i])
            greekvalue = ''.join(greek.contents).lower()
            greekdict[greekkey] = greekvalue'''
