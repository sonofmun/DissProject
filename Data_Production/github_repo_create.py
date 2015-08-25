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
				params = {'name': 'Vol. {}'.format(d), 'description': 'Raw OCR for PG Volume {}'.format(d)}
				reply = requests.post(self.base, data=json.dumps(params), headers={'Authorization': self.auth})
				if reply.status_code == 201:
					os.chdir(os.path.join(self.orig, d))
					os.system('git init')
					with open('.gitignore', mode='w') as f:
						f.write(self.ignore)
					os.system('git add -A')
					os.system('git commit -m "initial commit"')
					os.system('git remote add origin https://{3}:{0}@github.com/{4}/Vol.-{1}.git'.format(self.auth.split()[1], d, self.uname, self.org))
					os.system('git push --set-upstream origin master')
				else:
					print('There was an error creating the repository Vol.-{}'.format(d))
					print(reply.text)