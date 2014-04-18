from txt_to_npy import Txt_to_nparray
import os.path
from tkinter.filedialog import askdirectory
orig_dir = askdirectory(title = 'Where are your original VSMs located?')
VSM_list = os.listdir(orig_dir)
for file in VSM_list:
    if not file.endswith('.txt'):
        VSM_list.remove(file)
for filename in VSM_list:
    dest_filename = ''.join([os.path.splitext(filename)[0], '_Abridged', os.path.splitext(filename)[1]])
    CS, lem_dict = Txt_to_nparray(filename)
    unsorted_dict = {}
    sorted_dict = {}
    abridged = {}
    '''The following produces an unsorted dictionary that contains a dictionary containing
    the index of the of the lemma in the original matrix, the count of that lemma in the
    corpus, and then every co-occurent and its relational value to the lemma
    in the original matrix.
    '''
    for lem in lem_dict:
        unsorted_dict[lem] = {'VSM_index': lem_dict[lem]['index'], 'count': lem_dict[lem]['count'], 'collocates': []}
        for name in CS.dtype.names:
            unsorted_dict[lem]['collocates'].append((name, CS[lem_dict[lem]['index']][name]))
    '''The following produces a sorted copy of the unsorted dictionary having the same structure
    but with the collocates being sorted according to their value.
    '''
    for word in unsorted_dict:
        sorted_dict[word] = {'VSM_index': lem_dict[word]['index'], 'count': lem_dict[word]['count']}
        sorted_dict[word]['collocates'] = sorted(unsorted_dict[word]['collocates'], key = lambda x: x[1])
    '''The following produces an abridged version of the sorted_dict that only contains two different lists
    one of the first and one of the last50 co-occurrents sorted by the value.
    This is to produce a text file that is smaller and more easily readable.
    '''
    for lem in sorted_dict:
        abridged[lem] = {'count': sorted_dict[lem]['count']}
        abridged[lem]['collocates'] = []
        abridged[lem]['collocates'].append(sorted_dict[lem]['collocates'][:49])
        abridged[lem]['collocates'].append(sorted_dict[lem]['collocates'][-50:])
    with open(dest_filename, mode = 'w', encoding = 'utf-8') as file:
        file.write(','.join(['Lemma', 'Lemma Count', 'Co-occurrent', 'Co-occurent Value']) + '\n')
        for lemma in abridged:
            file.write(','.join([lemma, str(abridged[lemma]['count'])]) + '\n')
            for coll in abridged[lemma]['collocates'][0]:
                file.write(','.join([' ', ' ', coll[0], str(coll[1])]) + '\n')
            file.write('\n')
            for coll in abridged[lemma]['collocates'][1]:
                file.write(','.join([' ', ' ', coll[0], str(coll[1])]) + '\n')
