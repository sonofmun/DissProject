import re
orig_file = open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\XML\ParallelBible\par_bible.txt', mode = "r", encoding = 'utf-8')
of_list = orig_file.readlines()
orig_file.close()
dest_list_file = open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\XML\ParallelBible\new_par_bible.txt', mode = 'r', encoding = 'utf-8')
dest_list = dest_list_file.readlines()
dest_list_file.close()
dest_file = open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\XML\ParallelBible\new_par_bible.txt', mode = 'a', encoding = 'utf-8')
last_english = ''
counter = 0
for line in of_list:
    try:
        if dest_list[counter]:
            counter += 1
            continue
    except IndexError as N:
        elements = re.search(r'<w id="[A-Za-z0-9]{3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" eng="([^"]*)">([^<]*)</w>', line)
        english = elements.group(1)
        greek = elements.group(2)
        if english.isupper():
            if english == last_english and len(english.split()) == 2:
                new_english = english.strip(last_new_english)
                new_english = new_english.strip()
            else:
                new_english = input('What should the English translation be? Greek:' + greek + ' English: ' + english + ' ')
            newer_english = ''.join(['eng="', new_english, '">']) 
            line = re.sub(r'eng="([^"]*)">', newer_english, line)
            last_new_english = new_english
        last_english = english
        print(line)
        dest_file.write(line) #for some reason, this is not writing to the file.  I need to figure out why.  It could be something with the append mode.
dest_file.close()
