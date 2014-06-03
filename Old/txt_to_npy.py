def Txt_to_nparray(filename):
    import numpy as np
    with open(filename, encoding = 'utf-8') as file:
        #CS_list = file.readlines()
        #CS_list = []
        lem_dict = {}
        for i, line in enumerate(file):
            if i == 0:
                heading = line.rstrip('\n').replace("'", '').split(',')
                del heading[:2]
                formats = ['float' for x in heading]
                VSM = np.recarray(len(heading), dtype = {'names': heading, 'formats': formats})
            else:
                item = line.rstrip('\n').replace("'", '').split(',')
                #print(item[0])
                lem = item.pop(0)
                #print(item[0])
                count = int(item.pop(0))
                lem_dict[lem] = {'index': i-1, 'count': count}
                try:
                    VSM[i-1] = tuple(item)
                except IndexError as E:
                    print(i-1)
                    print(len(VSM))
                #CS_list.append(line.rstrip('\n').replace("'", '').split(','))
        #heading = CS_list.pop(0)
        #del heading[:2]
        #formats = ['float' for x in heading]
        #lem_dict = {}
        #for i, line in enumerate(CS_list):
            #lem = line.pop(0)
            #count = int(line.pop(0))
            #lem_dict[lem] = {'index': i, 'count': count}
        #VSM = np.recarray(len(CS_list), dtype = {'names': heading, 'formats': formats})
        #for i, item in enumerate(CS_list):
            #VSM[i] = tuple(item)
    return VSM, lem_dict
