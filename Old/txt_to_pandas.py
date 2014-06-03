def empty_df(line):
    import pandas as pd
    heading = line.rstrip('\n').replace("'", '').split(',')
    del heading[:2]
    df = pd.DataFrame(data = 0, index = heading, columns = heading)
    return df
def lem_dict_creator(filename):
    with open(filename, encoding = 'utf-8') as file:
        lem_dict = {}
        for i, line in enumerate(file):
            if i == 0:
                continue
            else:
                item = line.rstrip('\n').replace("'", '').split(',')
                #print(item[0])
                lem = item.pop(0)
                #print(item[0])
                count = int(item.pop(0))
                lem_dict[lem] = {'index': i-1, 'count': count}
    return lem_dict
def Txt_to_DataFrame(filename):
    import pandas as pd
    with open(filename, encoding = 'utf-8') as file:
        for i, line in enumerate(file):
            if i == 0:
                df = empty_df(line)
            else:
                item = line.rstrip('\n').replace("'", '').split(',')
                del item[:2]
                try:
                    df.ix[:, i-1] = tuple(item)
                except IndexError as E:
                    print(i-1)
                    print(len(df))
    return df
