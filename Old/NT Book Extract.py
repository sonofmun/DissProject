import re
input_file = open(r'C:\CompLing\GBible\UTF8\NTGreekUnicode.txt', mode = 'r', encoding = 'utf-8')
input_list = input_file.readlines()
input_file.close()
paul_list = ['Rom', '1Co', '2Co', 'Gal', '1Th', 'Phm', 'Phi']
non_paul_list = ['Act', 'Heb', '2Jo', 'Jam', '1Jo', '1Pe', 'Jud', '2Pe', 'Rev', '1Jo']
for line in input_list:
    line_parts = re.search(r'([A-Za-z0-9]{3}) [0-9]{1,3}:[0-9]{1,3} ([^\n]+\n)', line)
    try:
        book = line_parts.group(1)
    except AttributeError as E:
        continue
    try:
        text = line_parts.group(2)
    except AttributeError as E:
        continue
    if book in paul_list:
        with open(r'C:\CompLing\GBible\UTF8\NTPaul_Unicode.txt', mode = 'a+', encoding = 'utf-8') as paul_file:
            paul_file.write(text)
        file_name = ''.join(['C:/CompLing/GBible/UTF8/NTPaul_', book, 'Unicode.txt'])
    elif book in non_paul_list:
        with open(r'C:\CompLing\GBible\UTF8\NTNonPaul_Unicode.txt', mode = 'a+', encoding = 'utf-8') as non_paul_file:
            non_paul_file.write(text)
        file_name = ''.join(['C:/CompLing/GBible/UTF8/NonPaul_', book, 'Unicode.txt'])
    else:
        file_name = ''.join(['C:/CompLing/GBible/UTF8/UNK_', book, '_Unicode.txt'])
    with open(file_name, mode = 'a+', encoding = 'utf-8') as book_file_name:
        book_file_name.write(line)
