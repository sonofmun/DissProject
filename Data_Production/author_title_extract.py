__author__ = 'matt'

from lxml import etree
import json
from glob import glob
from os.path import basename


class get_local:
    def __init__(self, orig, base):
        self.base = base
        with open(orig) as f:
            self.lines = f.read().split('\n')

    def construct_dicts(self):
        with open(
                '{}/canonical-greekLit/canonical-greekLit.tracking.json'.format(
                        self.base)) as f:
            self.j = json.load(f)
        self.m = {}
        for k in self.j.keys():
            try:
                self.m[self.j[k]['id']] = k
            except KeyError:
                continue

    def extract(self):
        new_lines = []
        for line in self.lines:
            try:
                id = line.split('-')[2]
            except IndexError:
                new_lines.append(line)
                continue
            p = self.base + '/' + self.j[self.m[id]]['target']
            try:
                root = etree.parse(p).getroot()
            except OSError:
                new_lines.append('{0},{1}'.format(p, line))
                continue
            except:
                print(p)
                continue
            if root.nsmap:
                namespace = {root.tag.split('}')[-1]: root.nsmap[None]}
                prefix = '{}:'.format(root.tag.split('}')[-1])
            else:
                namespace = {}
                prefix = ''
            try:
                title = root.xpath('//{0}titleStmt/{0}title'.format(prefix),
                                   namespaces=namespace)[0].text.strip()
            except IndexError:
                title = 'No Title'
            try:
                author = root.xpath('//{0}titleStmt/{0}author'.format(prefix),
                                    namespaces=namespace)[0].text.strip()
            except IndexError:
                author = 'No Author'
            if 'New Testament' not in title:
                new_lines.append('{0},{1},{2}'.format(author, title, line))
        new_lines[0] = 'Author,Work,{}'.format(self.lines[0])
        return new_lines

class from_files:

    def __init__(self, orig_dir, cts_dir, dest_file):
        """

        :param orig_dir: the directory in which the files are contained
        :type orig_dir: str
        :param cts_dir: the directory where the __cts__.xml files can be found
        :type cts_dir: str
        :param dest_file: the file into which the tab-delimited data will be saved
        :type dest_file: str
        :return: the authors and names of the works of the files in orig_dir
        :rtype: tab-delimited TSV text file
        """
        self.files = glob('{}/*.txt'.format(orig_dir))
        self.cts = cts_dir
        self.dest = dest_file

    def extractIDs(self):
        """
        extracts the author and work ids from the filenames
        :return: author and works ids
        :rtype: list of lists with strings
        """
        for i, f in enumerate(self.files):
            self.files[i] = basename(f).split('.')[:2]

    def get_author(self, author_id):
        """
        extracts author name from the appropriate __cts__.xml file
        :param author_id: the URN for the author
        :type author_id: str
        :return: author name
        :rtype: str
        """
        return etree.parse('{}/{}/__cts__.xml'.format(self.cts, author_id)).getroot().xpath('/ti:textgroup/ti:groupname', namespaces={'ti': 'http://chs.harvard.edu/xmlns/cts'})[0].text

    def get_work(self, author_id, work_id):
        """
        extracts work name from the appropriate __cts__.xml file
        :param author_id: the URN for the author
        :type author_id: str
        :param work_id: the URN for the work
        :type work_id: str
        :return: work name
        :rtype: str
        """
        return etree.parse('{}/{}/{}/__cts__.xml'.format(self.cts, author_id, work_id)).getroot().xpath('/ti:work/ti:title', namespaces={'ti': 'http://chs.harvard.edu/xmlns/cts'})[0].text

    def append_names(self):
        """
        appends the author and work names to the appropriate member of self.files
        :return: new copy of self.files with author and work names
        :rtype: list of lists with strings
        """
        for i, [author, work] in enumerate(self.files):
            try:
                self.files[i].append(self.get_author(author))
            except:
                self.files[i].append(author)
            try:
                self.files[i].append(self.get_work(author, work))
            except:
                self.files[i].append(work)

    def write_tsv(self):
        """
        writes the author and works names to tab-delimited text file
        :return: list of author and work names
        :rtype: tab-delimited text file
        """
        with open(self.dest, mode='w') as f:
            f.write('Author\tWork\n')
            [f.write('{}\t{}\t{}\t{}\n'.format(x[0], x[1], x[2], x[3])) for x in self.files]