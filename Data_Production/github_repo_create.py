__author__ = 'matt'

import os
import requests
import json


class CreateRepo:
    def __init__(self, token, orig, uname, ignore):
        self.base = 'https://api.github.com/orgs/OGL-PatrologiaGraecaDev/repos'
        self.auth = 'token {0}'.format(token)
        self.orig = orig
        self.uname = uname
        self.ignore = ignore

    def createrepos(self):
        raise NotImplementedError


class Organization(CreateRepo):
    def __init__(self, org, token, orig, uname, ignore):
        self.org = org
        self.base = 'https://api.github.com/orgs/{}/repos'.format(org)
        self.auth = 'token {0}'.format(token)
        self.orig = orig
        self.uname = uname
        self.ignore = ignore

    def createrepos(self):
        dirs = os.listdir(self.orig)
        for d in dirs:
            if os.path.isdir(os.path.join(self.orig, d)):
                params = {'name': 'Vol. {}'.format(d),
                          'description': 'Raw OCR for PG Volume {}'.format(d)}
                reply = requests.post(self.base, data=json.dumps(params),
                                      headers={'Authorization': self.auth})
                if reply.status_code == 201:
                    os.chdir(os.path.join(self.orig, d))
                    os.system('git init')
                    with open('.gitignore', mode='w') as f:
                        f.write(self.ignore)
                    os.system('git add -A')
                    os.system('git commit -m "initial commit"')
                    os.system(
                        'git remote add origin https://{3}:{0}@github.com/{4}/Vol.-{1}.git'.format(
                            self.auth.split()[1], d, self.uname, self.org))
                    os.system('git push --set-upstream origin master')
                else:
                    print(
                        'There was an error creating the repository Vol.-{}'.format(
                            d))
                    print(reply.text)

class Issue(CreateRepo):
    def __init__(self, org, repo, token, orig, uname, ignore):
        """

        :param org:
        :type org:
        :param repo:
        :type repo:
        :param token: Github OAuth token (in the form, e.g., 97cc6b...1102ba)
        :type token:
        :param orig:
        :type orig:
        :param uname:
        :type uname:
        :param ignore:
        :type ignore:
        """

        # self.org = org
        self.base = 'https://api.github.com/repos/{}/{}/issues'.format(org, repo)
        self.auth = 'token {0}'.format(token)
        self.orig = orig
        self.uname = uname
        self.ignore = ignore
        self.problems = []

    def createissues(self):
        with open(self.orig) as f:
            issues = [x for x in f.read().split('\n')]
        for i in issues:
            issue = i.split('\t')
            params = {'title': issue[0], 'body': issue[1]}
            reply = requests.post(self.base, data=json.dumps(params),
                                  headers={'Authorization': self.auth})
            if reply.status_code != 201:
                self.problems.append('{} {}: {}'.format(issue[0], issue[1], reply.text))