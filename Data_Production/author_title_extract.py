__author__ = 'matt'

from lxml import etree
import json


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