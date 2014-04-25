from txt_to_npy import Txt_to_nparray
import os.path
from tkinter.filedialog import askdirectory
import pickle
orig_dir = askdirectory(title = 'Where are your original VSMs located?')
VSM_list2 = os.listdir(orig_dir)
VSM_list = []
for file in VSM_list2:
    if 'Abridged' not in file and file.endswith('.txt'):
        VSM_list.append(file)
for file in VSM_list:
    filename = os.path.join(orig_dir, file)
    dest_filename = ''.join([os.path.splitext(filename)[0], '.pickle'])
    dict_filename = ''.join([os.path.splitext(filename)[0], '_lem_dict.pickle'])
    CS, lem_dict = Txt_to_nparray(filename)
    with open(dest_filename, mode = 'wb') as file:
        pickle.dump(CS, file)
    with open(dict_filename, mode = 'wb') as file:
        pickle.dump(lem_dict, file)
        
