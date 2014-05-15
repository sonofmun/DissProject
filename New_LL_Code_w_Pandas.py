'''
To apply the log-likelihood function to every cell in a pandas DataFrame
use df.apply(function).  The function can then call the name and index of
the cell you are working on, and thus call values from other DataFrames
'''
import pandas as pd
C1 = deci.Decimal(LemCount) #this is the number of occurrences of the word under investigation
C2 = deci.Decimal(CollLemCount) #this is the number of times the co-occurrent occurs in the corpus
C12 = deci.Decimal(CollCount.astype(deci.Decimal)/8) #this is the number of times the original word and the co-occurrent occur together.  I divide by 8 because the number of occurrences is spread over a collocation window 8 words wide.
def log_like(cell):
    #The log-likelihood calculator to be called by df.apply()
    w1 = x.index
    w2 = x.name
    return LL
def num_counter(lem_dict):
    #calculates the total number of words in the corpus from the lem_dict
    return num_count
def lem_counter(lemma):
    #retrieves the count of the lemma under question
    return lem_count

LL_df = Coll_df.apply(lambda x: log_like(x))
#produce count Series (lemmas and counts) from the lem_dict
#then simply apply that to each row in the df
#so whenever I need the count of word 2 in the calculation, simply input this Series
#The problem to solve now, however, is how to get the count of the indices in there
#I will have to figure this out
