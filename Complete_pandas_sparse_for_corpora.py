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
from tkinter.filedialog import asksaveasfilename, askopenfilename
#load np.recarray and pandas sparse DataFrame
corp_VSM_file = askopenfilename(title = 'Where is your corpora VSM file?')
lem_sparse_file = askopenfilename(title = 'Where is your sparse DataFrame with LXX lemmata?')
#load lem_dict for the corpus
lem_dict_file = askopenfilename(title = 'Where is your dictionary of lemmas for this corpus?')
dest_file = asksaveasfilename(title = 'Where would you like to save the resulting pickle file?')
corp_VSM = pandas.read_pickle(corp_VSM_file)
lem_sparse = pandas.read_pickle(lem_sparse_file)
lem_dict = pandas.read_pickle(lem_dict_file)
#convert np.array to a pandas DataFrame producing indices from the lem_dict values
corp_DF = pandas.DataFrame(data = corp_VSM, index = lem_dict.keys(), columns = lem_dict.keys(), dtype = float)
#The above assumes that the column names will not be taken from the np.recarray
corp_full_DF = corp_DF.combine_first(lem_sparse)
#convert the full_DataFrame to a sparse Data_Frame
corp_full_sparse = corp_full_DF.to_sparse()
#to_pickle
corp_full_sparse.to_pickle(dest_file)
