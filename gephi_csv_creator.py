def build_csv(orig, d, lim):
    import pandas as pd
    df_edge = pd.DataFrame(index = [0], columns = ['Source', 'Target', 'Weight', 'Type'])
    s_node = pd.Series()
    counter = 0
    words = []
    for word, occ in d.items():
        if occ >= lim:
            words.append(word)
    for i, word in enumerate(words):
        s_node.ix[word] = d[word]
        for word2 in orig.ix[word].index:
            df_edge.ix[counter] = (word, word2, 1-orig_new[word][word2], 'undirected')
            #s = pd.Series(data = (word, word2, orig.ix[word, word2]), index = ['Source', 'Target', 'Weight'])
            #dest.append(s)
            counter += 1
    return df_edge, s_node
