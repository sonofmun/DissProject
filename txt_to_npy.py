def Txt_to_nparray(filename):
    import numpy as np
    with open(filename, encoding = 'utf-8') as file:
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
