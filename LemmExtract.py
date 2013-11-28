import re
with open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\XML\GreekBibleLemmLXX.txt', mode ='r', encoding = 'utf-8') as f:
    for line in f:
        lemlist = re.findall(r'lem=\"[^\"]+\"', line)
        for lemma in lemlist:
            #print(lemma)
        #newline = re.sub(r'[\S]+ [\S]+ [\S]+ lem="([^\"])+"[\S]\n', '\1', line)
            newlem = re.sub(r'lem=\"([^\"]+)\"', r'\1', lemma)
            newlem += '\n'
            #print(newlem)
            with open(r'C:\Users\matthew.munson\Google Drive\Dissertation\CompLing\GBible\XML\GreekBibleLXXOnlyLems.txt', mode = 'a+', encoding = 'utf-8') as f2:
                f2.write(newlem)
