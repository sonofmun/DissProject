'''
Created on 22.08.2012

@author: matthew.munson
'''
import re
source = open('C:\CompLing\GBible\BWConversion_Dirty.txt', 'r', encoding='utf-8') #put the file to be used as the source here
destination = open('C:\CompLing\GBible\BWConversion_Upper.txt', 'w', encoding='utf-8') #put the path to the destination file here
#ignoreline = re.compile(r'(^Origenes sec\.|^Cl\. 0198|^[0-9]{1,4})')
retab = re.compile(r'\t')
newlinedel = re.compile(r'\n')
for line in source:
    #ignoreline = re.search(r'(^Origenes secundum|^Cl\. 0198|^[0-9]{1,4}\n|^\t)', line)
    #print(line)
    line = line.replace('\'', '\\\'')
    line = retab.sub('\': \'', line)
    line = newlinedel.sub('\', \'', line)
    line = line.upper()
    #print(line)
    #line.replace('\t', ': \'')
    destination.write(line)
destination.close()
source.close()