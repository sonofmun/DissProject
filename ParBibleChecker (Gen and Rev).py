import re
orig_file = open(r'..\..\..\..\XML\ParallelBible\par_bible.txt', mode = "r", encoding = 'utf-8')
of_list = orig_file.readlines()
orig_file.close()
try:
    with open(r'..\..\..\..\XML\ParallelBible\par_Gen.txt', mode = 'r', encoding = 'utf-8') as Gen_list_file:
        Gen_list = Gen_list_file.readlines()
except FileNotFoundError as N:
    Gen_list = []
try:
    with open(r'..\..\..\..\XML\ParallelBible\par_Act.txt', mode = 'r', encoding = 'utf-8') as Act_list_file:
        Act_list = Act_list_file.readlines()
except FileNotFoundError as N:
    Act_list = []
#dest_file = open(r'..\..\..\..\XML\ParallelBible\new_par_bible.txt', mode = 'a+', encoding = 'utf-8')
last_english = ''
counter = 0
for line in of_list:
    elements = re.search(r'<w id="([A-Za-z0-9]{3})\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" eng="([^"]*)">([^<]*)</w>', line)
    book = elements.group(1)
    if book == 'Gen' or book == 'Act':
        if book == 'Gen':
            dest_list = Gen_list
        else:
            dest_list = Act_list
        try:
            if dest_list[counter]:
                counter += 1
                continue
        except IndexError as N:
            english = elements.group(2)
            greek = elements.group(3)
            if english.isupper():
                if english == last_english and len(english.split()) == 2:
                    if greek == 'ο':
                        new_english = ''
                    else:
                        new_english = english.lower().replace(last_new_english, '')
                        new_english = new_english.strip()
                        last_new_english = new_english
                else:
                    new_english = input('What should the English translation be? Greek:' + greek + ' English: ' + english + ' ')
                    last_new_english = new_english
                newer_english = ''.join(['eng="', new_english, '">']) 
                line = re.sub(r'eng="([^"]*)">', newer_english, line)
            last_english = english
            print(line)
            file_name = ''.join([r'..\..\..\..\XML\ParallelBible\par_', book, '.txt'])
            with open(file_name, mode = 'a+', encoding = 'utf-8') as dest_file:
                dest_list = dest_file.readlines()
                if line in dest_list:
                    continue
                else:
                    dest_file.write(line)
