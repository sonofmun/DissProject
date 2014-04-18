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
