Python 3.3.2 (v3.3.2:d047928ae3f6, May 16 2013, 00:06:53) [MSC v.1600 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> TestFile = open('C:/Users/mam3tc/Google Drive/Dissertation/CompLing/GBible/LouwNidaDict.txt', mode='r', encoding='UTF-8')
>>> TestFile.readline()
"{'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],\n"
>>> TestFile.readline()
"'ψεύδομαι': [33, 'Communication', '33R Speak Truth, Speak Falsehood', 'lie', '33.253'],\n"
>>> TestFile = open('C:/Users/mam3tc/Google Drive/Dissertation/CompLing/GBible/LouwNidaDict.txt', mode='r', encoding='UTF-8')
>>> TestList = TestFile.readlines()
>>> TestList[0]
"{'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],\n"
>>> import re
>>> Dictionary = {}
>>> for line in TestList:
	strippedline = line.strip('{}\n')
	DictKey = re.match(r"\'[^\']\'", strippedline)
	DictValue = re.search(r"\[[^\]]]", strippedline)
	Dictionary[DictKey] = DictValue

	
>>> Dictionary[DictKey]
>>> len(Dictionary)
5
>>> Dictionary.popitem()
(None, None)
>>> teststrip = TestList[0].strip('{}\n')
>>> teststrip
"'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],"
>>> testkey = re.match(r"\'[^\']\'", teststrip)
>>> testkey
>>> testkey = re.match(r"\'[^:]\'", teststrip)
>>> testkey
>>> testkey = re.match(r"[^:]", teststrip)
>>> testkey
<_sre.SRE_Match object at 0x000000000312BAC0>
>>> print(testkey)
<_sre.SRE_Match object at 0x000000000312BAC0>
>>> str(testkey)
'<_sre.SRE_Match object at 0x000000000312BAC0>'
>>> testkey.string()
Traceback (most recent call last):
  File "<pyshell#32>", line 1, in <module>
    testkey.string()
TypeError: 'str' object is not callable
>>> testkey
<_sre.SRE_Match object at 0x000000000312BAC0>
>>> testkey.string
"'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],"
>>> testkey = re.match("[^:]", teststrip)
>>> testkey.string
"'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],"
>>> testkey = re.match("[^\:]", teststrip)
>>> testkey.string
"'ἐκζητέω': [27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],"
>>> testkey = re.split(":", teststrip)[0]
>>> testkey
"'ἐκζητέω'"
>>> testvalue = re.split(": ", teststrip)[1]
>>> testvalue
"[27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9'],"
>>> testvalue = re.split(": ", teststrip)[1].strip(',')
>>> testvalue
"[27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9']"
>>> Dictionary[testkey] = testvalue
>>> Dictionary = {}
>>> Dictionary[testkey] = testvalue
>>> Dictionary
{"'ἐκζητέω'": "[27, 'Learn', '27D Try To Learn', 'a seek diligently', '27.35', 56, 'Courts and Legal Procedures', '56C Accusation', 'b bring charges against', '56.9']"}
>>> testvalue = list(re.split(": ", teststrip)[1].strip(','))
>>> testvalue
['[', '2', '7', ',', ' ', "'", 'L', 'e', 'a', 'r', 'n', "'", ',', ' ', "'", '2', '7', 'D', ' ', 'T', 'r', 'y', ' ', 'T', 'o', ' ', 'L', 'e', 'a', 'r', 'n', "'", ',', ' ', "'", 'a', ' ', 's', 'e', 'e', 'k', ' ', 'd', 'i', 'l', 'i', 'g', 'e', 'n', 't', 'l', 'y', "'", ',', ' ', "'", '2', '7', '.', '3', '5', "'", ',', ' ', '5', '6', ',', ' ', "'", 'C', 'o', 'u', 'r', 't', 's', ' ', 'a', 'n', 'd', ' ', 'L', 'e', 'g', 'a', 'l', ' ', 'P', 'r', 'o', 'c', 'e', 'd', 'u', 'r', 'e', 's', "'", ',', ' ', "'", '5', '6', 'C', ' ', 'A', 'c', 'c', 'u', 's', 'a', 't', 'i', 'o', 'n', "'", ',', ' ', "'", 'b', ' ', 'b', 'r', 'i', 'n', 'g', ' ', 'c', 'h', 'a', 'r', 'g', 'e', 's', ' ', 'a', 'g', 'a', 'i', 'n', 's', 't', "'", ',', ' ', "'", '5', '6', '.', '9', "'", ']']
>>> testvalue = list(re.split(": ", teststrip)[1].strip(',[]').split(','))
>>> testvalue
['27', " 'Learn'", " '27D Try To Learn'", " 'a seek diligently'", " '27.35'", ' 56', " 'Courts and Legal Procedures'", " '56C Accusation'", " 'b bring charges against'", " '56.9'"]
>>> testvalue = list(re.split(": ", teststrip)[1].strip(',[]').split(', '))
>>> testvalue
['27', "'Learn'", "'27D Try To Learn'", "'a seek diligently'", "'27.35'", '56', "'Courts and Legal Procedures'", "'56C Accusation'", "'b bring charges against'", "'56.9'"]
>>> 
