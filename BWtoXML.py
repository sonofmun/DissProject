'''
Created on 19.12.2012

This script takes a .txt file input in BibleWorks Greek Beta Code with lemma information and companion text
and converts it to XML.
It requires that the BWGtoUnicode.py and the UnicodeToXMLLemmas.py are in the same directory from which 
this file is executed.

@author: matthew.munson
'''
import re
import BWGtoUnicode
import UnicodeToXMLLemmas
print("Please use forward slashes / instead of backslashes \ in your paths.")
sourcepath = input("What is the full path of the BW Beta Code source file (should be a .txt file)?")
destpath = input("What is the full path of the directory where you wish your XML Unicode destination file to be created?")
rawpath = re.sub(".[txTX]{3}", "", sourcepath)
filename = re.search(r"\w+.[txTX]{3}", sourcepath)
rawfilename = re.sub(".[txTX]{3}", "", filename.group(0))
unicodedest = rawpath + "Unicode.txt"
xmldest = destpath + "/" +  rawfilename + "XML" + ".txt"
BWGtoUnicode.BWGtoUnicode(sourcepath, unicodedest)
UnicodeToXMLLemmas.UnicodeToXML(unicodedest,xmldest)