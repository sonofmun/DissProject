#from txt_to_npy import Txt_to_nparray
import os.path
from tkinter.filedialog import askdirectory
import pandas as pd
import datetime

orig_dir = askdirectory(title = 'Where are your original VSMs located?')
dicts = askdirectory(title = 'Where are your lem_dict pickles located?')
dest_dir = askdirectory(title = 'Where would you like to save the resulting CSV files?')
VSM_list = sorted([x for x in os.listdir(orig_dir) if x.endswith('pickle')])
dicts_list = sorted([x for x in os.listdir(dicts) if x.endswith('pickle')])
if len(VSM_list) > len(dicts_list):
    dicts_list *= len(VSM_list)//len(dicts_list)
    dicts_list = sorted(dicts_list)
files = zip(VSM_list, dicts_list)

for file, lem_dict in files:
    print('Analyzing %s at %s' % (file, datetime.datetime.now().time().isoformat()))
    filename = os.path.join(orig_dir, file)
    dictname = os.path.join(dicts, lem_dict)
    dest_file = ''.join([os.path.splitext(file)[0], '_Abridged.csv'])
    dest_filename = '/'.join([dest_dir, dest_file])
    if os.path.isfile(dest_filename):
        continue
    else:
        orig = pd.read_pickle(filename)
        lem_dict = pd.read_pickle(dictname)
        abridged = {}
        
        for lem in orig.index:
            abridged[lem] = {'count': lem_dict[lem]}
            abridged[lem]['collocates'] = []
            ser = orig.ix[lem]
            ser.sort()
            abridged[lem]['collocates'].append(ser[:50])
            abridged[lem]['collocates'].append(ser[-50:])
        with open(dest_filename, mode = 'w', encoding = 'utf-8') as file:
            file.write(','.join(['Lemma', 'Lemma Count', 'Co-occurrent', 'Co-occurent Value']) + '\n')
            for lemma in sorted(abridged.keys()):
                file.write(','.join([lemma, str(abridged[lemma]['count'])]) + '\n')
                for coll, count in abridged[lemma]['collocates'][0].iteritems():
                    file.write(','.join([' ', ' ', coll, str(count)]) + '\n')
                file.write('...\n')
                for coll, count in abridged[lemma]['collocates'][1].iteritems():
                    file.write(','.join([' ', ' ', coll, str(count)]) + '\n')
