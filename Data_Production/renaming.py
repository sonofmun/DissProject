__author__ = 'matt'

from glob import glob
import os

d_dir = '/media/matt/INTENSO/Dissertation/Diss_Data/XML'

for orig in glob('{0}/*'.format(d_dir)):
	if os.path.isdir(orig):
		for final in ('COOC', 'CS', 'PPMI'):
			for file in glob('{0}/{1}/*.pickle'.format(orig, final)):
				p, s = os.path.split(file)
				l = s.replace('.pickle', '').split('_')
				w = os.path.basename(orig)
				new_s = '{0}_{1}_{2}_{3}.pickle'.format(l[2], w, l[0], l[1])
				print('{0}/{1}'.format(orig, new_s))
				os.rename(file, '{0}/{1}'.format(orig, new_s))