__author__ = 'matt'
'''
The purpose of this script is to control Tkinter filedialog instances.
'''

from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory, asksaveasfilename

def tk_control(c):
	root = Tk()
	root.withdraw()
	x = eval(c)
	root.destroy()
	return x