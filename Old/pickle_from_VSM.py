from txt_to_pandas import Txt_to_DataFrame, lem_dict_creator
from pickle import dump
import os.path
def file_chooser():
    from tkinter.filedialog import askdirectory
    orig_dir = askdirectory(title = 'Where are your original VSMs located?')
    VSM_list2 = os.listdir(orig_dir)
    VSM_list = []
    for file in VSM_list2:
        if 'Abridged' not in file and file.endswith('.txt'):
            VSM_list.append(file)
    return VSM_list, orig_dir
def lem_dict_dump(fn, dict_fn):
    lem_dict = lem_dict_creator(fn)
    with open(dict_fn, mode = 'wb') as file:
        dump(lem_dict, file)
def df_dump(fn, df_fn):
    CS = Txt_to_DataFrame(fn)
    with open(df_fn, mode = 'wb') as file:
        dump(CS, file)
VSM_list, orig_dir = file_chooser()
for file in VSM_list:
    filename = os.path.join(orig_dir, file)
    dest_filename = ''.join([os.path.splitext(filename)[0], '.pickle'])
    dict_filename = ''.join([os.path.splitext(filename)[0], '_lem_dict.pickle'])
    lem_dict_dump(filename, dict_filename)
    df_dump(filename, dest_filename)
