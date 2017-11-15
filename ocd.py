# -*- coding: utf-8 -*-
'''
 ┌┬──────────────────────────────────┬┐
 └┤   OCD ANALYSIS SOFTWARE          ├┘
 ┌┤   Nick Charron - Huang Lab       ├┐
 └┤   Rice Univ - 2017               ├┘
 ┌┤   charron.nicholas.e@gmail.com   ├┐
 └┴──────────────────────────────────┴┘
'''
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import os

class ocd_spec:
	def renorm(self,scale_factor):
		self.cd = scale_factor*self.cd

	def load(self,fn):
		'''Specific to J810 ASCII'''
		data = np.loadtxt(fn,dtype=float,skiprows=19,usecols=(0,1,2))
		return data

	def __add__(self,new):
		new_ocd_spec = ocd_spec()
		cd = np.array([])
		for i,j in zip(self.cd,new.cd):
			cd = np.append(cd,i+j)
		new_ocd_spec.cd = cd
		new_ocd_spec.wl = self.wl
		return new_ocd_spec

	def __sub__(self,new):
		new_ocd_spec = ocd_spec()
		cd = np.array([])
		for i,j, in zip(self.cd,new.cd):
			cd = np.append(cd,i-j)
		new_ocd_spec.cd = cd
		new_ocd_spec.wl = self.wl

	def __rsub__(self,other):
		if other == 0:
			return self
		else:
			return self.__sub__(other)

	def __radd__(self,other):
		if other == 0:
			return self
		else:
			return self.__add__(other)

	def __init__(self,fn=None):
		if fn is not None:
			self.data = self.load(fn)
			'''Reverse Data'''
			self.wl = np.flipud(np.array(self.data[:,0]))
			self.cd = np.flipud(np.array(self.data[:,1]))
			self.name = fn
		if fn is None:
			self.data = np.array([[]])
			self.wl = np.array([])
			self.cd = np.array([])
			self.name = "empty spectrum"

	def graph(self):
		fig = plt.figure("CD Spectrum")
		plt.plot(self.wl, self.cd, 'k')
		plt.ylabel("CD [mdeg]")
		plt.xlabel("Wavelength [nm]")
		plt.show()

def avg_signal(specs):
	'''input is array of ocd_spec'''
	cd = np.zeros(len(specs[0].cd))
	for i in range(len(specs)):
		for j in range(len(specs[i].cd)):
			cd[j] += specs[i].cd[j]
	cd = cd/len(specs)
	avg = ocd_spec()
	avg.cd = cd
	avg.wl = specs[0].wl
	return avg

def mult_graph(specs,types=None,colors=None,widths=None,title=None):
	fig = plt.figure("Composite Plot")
	plt.title(title)
	plt.xlabel("Wavelength [nm]")
	plt.ylabel("CD [mdeg]")
	if types != None and colors == None:
		names=[]
		for i,j in zip(specs,types):
			plt.plot(i.wl,i.cd,j)
			names.append(i.name)
		plt.legend(names,loc="best")
		plt.show()
	if types != None and colors != None:
		names=[]
		for i,j,k in zip(specs,types,colors):
			plt.plot(i.wl,i.cd,j,color=k)
			names.append(i.name)
		plt.legend(names,loc="best")
		plt.show()
	if types == None and colors == None:
		names=[]
		for i in specs:
			plt.plot(i.wl,i.cd)
			names.append(i.name)
		plt.legend(names,loc="best")
		plt.show()
		
def graph_series(specs,title=None,cmap=mpl.cm.Reds):
	fig = plt.figure("Series Plot")
	plt.title(title)
	plt.xlabel("Wavelength [nm]")
	plt.ylabel("CD [mdeg]")
	names=[]
	for i in range(len(specs)):
		plt.plot(specs[i].wl,specs[i].cd,color=cmap((i+1)*1./len(specs)))
		names.append(specs[i].name)
	plt.legend(names,loc="best")
	plt.show()

if sys.platform == "win32":
	try:
		import wx

		def fs():
			app = wx.App(None)
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
			dialog = wx.FileDialog(None, 'Open',wildcard='*.txt',style=style)
			if dialog.ShowModal() == wx.ID_OK:
				path = dialog.GetPath()
			else:
				path = None
			dialog.Destroy()
			return ocd_spec(path)

	except:
		print("WX module not found. Defaulting to CLI.")
	
if sys.platform == "linux" or sys.platform == "darwin" \
or sys.platform == "linux2":
	try:
		from dialog import Dialog
		dlg = Dialog(dialog="dialog")
		
		def fs():
			rows, cols = os.popen("stty size","r").read().split()
			rows = int(rows); cols = int(cols)
			path = './'
			code, path = dlg.fselect('./',rows-30,cols-30,title="Select File")
			os.system("clear")
			print(path + " loaded.")
			return ocd_spec(path)
	except:
		print("Dialog module not found. Defaulting to CLI.")
		