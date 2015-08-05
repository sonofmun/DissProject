__author__ = 'matt'

import os
import requests
import json

class OGLPGCreate:

	def __init__(self, token, orig):
		self.base = 'https://api.github.com/orgs/OGL-PatrologiaGraecaDev/repos'
		self.auth = 'token {0}'.format(token)
		self.orig = orig

	def createrepos(self):
		dirs = os.listdir(self.orig)
		ignore = '*.png\n*.uzn'
		for d in dirs:
			if os.path.isdir(os.path.join(self.orig, d)):
				params = {'name': 'Vol. {}'.format(d), 'description': 'Raw OCR for PG Volume {}'.format(d)}
				reply = requests.post(self.base, data=json.dumps(params), headers={'Authorization': self.auth})
				if reply.status_code == 201:
					os.chdir(os.path.join(self.orig, d))
					os.system('git init')
					with open('.gitignore', mode='w') as f:
						f.write(ignore)
					os.system('git add -A')
					os.system('git commit -m "initial commit"')
					os.system('git remote add origin git@github.com:OGL-PatrologiaGraecaDev/Vol.-{}.git'.format(d))
					os.system('git push --set-upstream origin master')
				else:
					print('There was an error creating the repository Vol.-{}'.format(d))
					print(reply.text)