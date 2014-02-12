'''
Created on 14.02.2013

@author: matthew.munson
'''
import re
import pickle
import os
import math
import os.path
import decimal
lemdoc = open("C:/CompLing/GBible/XML/LemLists/GBibleLemmsNT.txt", mode = 'rb')
lemlist = pickle.load(lemdoc)
print(len(lemlist))
FileList = os.listdir("C:/CompLing/GBible/XML/CollLists/NT")
LemCount = 0
#CollPos = ['L10', 'L9', 'L8', 'L7', 'L6', 'L5', 'L4', 'L3', 'L2', 'L1', 'Lemma', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10']
for file in FileList:    
    LLCollList = []
    CollFilename = "C:/CompLing/GBible/XML/CollLists/NT/" + file
    CollFile = open(CollFilename, mode = 'r', encoding = 'utf-8')
    LLfile = re.sub(r'.txt', r'_LL.txt', file)
    LLFileName = "C:/CompLing/GBible/XML/CollLists/NT/LL/" + LLfile
    if os.path.isfile(LLFileName) == True: #checks to see if a collocation file already exists for this lemma
        continue #if a collocation file for this lemma exists, it breaks out of the if loop and selects the next member of lemlist
    else:
        LLListFile = open(LLFileName, mode = 'w', encoding = 'utf-8')
        for line in CollFile:
            if 'P=Lemma' in line:
                LemCount = int(re.sub(r'.+?Lemma W=[^\']+\', ([0-9]+).*\n', r'\1', line))
    #        CollIndex = 0
            if '(' in line:
                line = line.strip(',"\n') # = re.sub(r'\"', '', line, count = 1)
                LineList = re.split(r'\",+\"', line)
                for collocate in LineList:
                    if re.match('\",+\"', collocate):
                        continue
                    elif 'Lemma' in collocate:
                        LLLem = re.sub(r'\"{,1}\(\'(P=Lemma) (W=[^\']+)\', ([0-9]+)\)\"{,1}', r'(\1 \2 N=\3 MI=NA', collocate)
                        LLLem = LLLem + ')'
                        LLCollList.append(LLLem)
                        continue
                    else:
    #                    print(collocate)
                        CollCount = int(re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=[^\']+\', ([0-9]+)\)\"{,1}', r'\1', collocate))
                        CollLemCount = lemlist.count(re.sub(r'\"{,1}\(\'P=[LR][0-9]{1,2} W=([^\']+)\', [0-9]+\)\"{,1}', r'\1', collocate))
                        Num = len(lemlist)
                        C1 = decimal.Decimal(LemCount)
                        C2 = decimal.Decimal(CollLemCount)
                        C12 = decimal.Decimal(CollCount)
                        P = decimal.Decimal(C2/Num)
                        P1 = decimal.Decimal(C12/C1)
                        P2 = decimal.Decimal((C2 - C12)/(Num-C1))
                        Test = C2-C12
#                        print(P)
#                        print(Test)
#                        print(decimal.Context(Emin = -425000000).power(P, C2-C12))
#                        print(collocate)
                        LL1 = decimal.Context(Emin = -425000000).log10(decimal.Context(Emin = -425000000).power(P, C12)*decimal.Context(Emin = -425000000).power(1-P, C1-C12))
                        LL2 = decimal.Context(Emin = -425000000).log10(decimal.Context(Emin = -425000000).power(P, C2-C12)*decimal.Context(Emin = -425000000).power(1-P, Num-C1-C2-C12))
                        if P1 == 1:
                            LL3 = 0
                        else:
                            LL3 = decimal.Context(Emin = -425000000).log10(decimal.Context(Emin = -425000000).power(P1, C12)*decimal.Context(Emin = -425000000).power(1-P1, C1-C12))
                        if P2 == 0:
                            LL4 = 0
                        else:
                            LL4 = decimal.Context(Emin = -425000000).log10(decimal.Context(Emin = -425000000).power(P2, C2-C12)*decimal.Context(Emin = -425000000).power(1-P2, (Num-C1)-(C2-C12)))
                        LL = -2*(LL1+LL2-LL3-LL4)
                        LLColl = re.sub(r'\"{,1}\(\'(P=[LR][0-9]{1,2}) (W=[^\']+)\', ([0-9]+)\)\"{,1}', r'(\1 \2 N=\3 LL=', collocate)
                        LLColl = LLColl + str(LL) + ')'
                        LLCollList.append(LLColl)
        LLCollStr = str(LLCollList)
        LLListFile.write(LLCollStr)
        LLListFile.close()
lemdoc.close()