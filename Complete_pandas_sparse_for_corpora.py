'''
The purpose of this file is to create a new pandas DataFrame from the
np.recarray of each corpus and the sparse DataFrame of the complete LXX lemmas.
This will produce a DataFrame where the values of the original np.array
are still in the frame but the words that are missing are filled in with
nan values.  This will allow the CS similarity calculation between different
corpora
'''
import numpy
import pandas
#load np.recarray and pandas sparse DataFrame
#load lem_dict for the corpus
#convert np.array to a pandas DataFrame producing indices from the lem_dict values
#I assume that the row names will be taken from the np.recarray
#full_DataFrame = new_DataFrame.combine_first(old_DataFrame)
#convert the full_DataFrame to a sparse Data_Frame
#to_pickle
