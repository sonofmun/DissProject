def Txt_to_nparray(filename):
    import numpy as np
    with open(filename, encoding = 'utf-8') as file:
        CS_List = file.readlines()
    for i, line in enumerate(CS_list):
        CS_list[i] = line.rstrip('\n').replace("'", '').split(',')
    heading = CS_list.pop(0)
    del heading[:2]
    formats = ['float' for x in heading]
    #VSM = np.empty(len(CS_list), dtype = {'names': heading, 'formats': formats})
    lem_dict = {}
    for i, line in enumerate(CS_list):
        lem = line.pop(0)
        count = int(line.pop(0))
        lem_dict[lem] = {'index': i, 'count': count}
    #CS_iter = map(tuple, CS_list)
    VSM = np.core.records.fromrecords(CS_list, dtype = {'names': heading, 'formats': formats})
    return VSM
'''
        headstr = file.readline()
        headings = headstr.replace("'", '').rstrip('\n').split(',')
        print(len(headings))
        print(len(set(headings)))
        print(set([x for x in headings if headings.count(x) > 1]))
        formats = ['<U30', 'int']
        [formats.append('float') for x in range(len(headings)-1)]
        mydescriptor = {'names': headings, 'formats': formats}
        print(len(headings))
        print(len(formats))
        cols_2_use = range(2, len(headings)-3)
        VSM = np.empty(len(headings)-2, dtype = mydescriptor)
        for i, row in enumerate(file.readlines()):
            VSM[i] = row
        #LLVSM = loadtxt(file, delimiter = ',', dtype = mydescriptor)
        print('finished')
'''
