def Txt_to_nparray(filename):
    import numpy as np
    with open(filename, encoding = 'utf-8') as file:
        CS_list = file.readlines()
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
    VSM = np.recarray(len(CS_list), dtype = {'names': heading, 'formats': formats})
    for i, item in enumerate(CS_list):
        VSM[i] = tuple(item)
    return VSM, lem_dict
'''
After running this, to get a list of (word, CS_Dist) that can later be sorted, do this:
sorted_dict = {}
for lem in lem_dict:
    lem_CS_vals = VSM[lem['index']]
    sorted_dict[lem] = []
    for name in VSM.dtype.names:
        sorted_dict[lem].append((name, VSM[lem['index']][name]))
'''
