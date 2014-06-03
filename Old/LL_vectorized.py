def log_like(row):
    import numpy as np
    #values for c1
    C1 = lem_counts[row.name] #this value will be the same throughout a whole row
    #values for c2
    #here I need a Series that has all the values for all of the words
    C2 = lem_counts
    #values for c12
    C12 = row #this is the row in the coll_df that I am looking at
    #values for p
    P = C2/N #N is the total number of words
    #values for p1
    P1 = C12/C1
    #values for p2
    P2 = (C2-C12)/(N-C1)
    LL1 = np.log(np.power(P, C12)*np.power(1-P, C1-C12))
    LL2 = np.log(np.power(P, C2-C12)*np.power(1-P, N-C1-C2-C12))
    try:
        LL3 = np.log(np.power(P1, C12)*np.power(1-P1, C1-C12))
    except deci.InvalidOperation as E:
        LL3 = 0
    try:
        LL4 = np.log(np.power(P2, C2-C12)*np.power(1-P2, (N-C1)-(C2-C12)))
    except deci.InvalidOperation as E:
        LL4 = 0
    LL = -2*(LL1+LL2-LL3-LL4)
    return LL
