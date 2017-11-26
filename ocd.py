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

def kaiser_smooth(x,beta):
    """ kaiser window smoothing """
    window_len=41              #Needs to be odd for proper response
                               # extending the data at beginning and at the end
                               # to apply the window at the borders
    s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]] #start:stop:step
    w = np.kaiser(window_len,beta)
    y = np.convolve(w/w.sum(),s,mode='valid')
    return y[20:len(y)-20]
    

class ocd_spec:
	def renorm(self,scale_factor):
		new_ocd_spec = ocd.spec()
		new_ocd_spec.wl = self.wl
		new_ocd_spec.dw = self.dw
		new_ocd_spec.name = self.name + "[Rescaled]"
		new_ocd_spec.cd = scale_factor*self.cd
		return new_ocd_spec

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
		return new_ocd_spec 

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
			self.dw = self.wl[0]-self.wl[1]
		if fn is None:
			self.data = np.array([[]])
			self.wl = np.array([])
			self.cd = np.array([])
			self.name = "empty spectrum"
			self.dw = None

	def graph(self):
		axis_y = np.zeros(len(self.wl))
		fig = plt.figure("CD Spectrum")
		plt.plot(self.wl, self.cd, 'k')
		plt.plot(self.wl, axis_y, 'k:')
		plt.ylabel("CD [mdeg]")
		plt.xlabel("Wavelength [nm]")
		plt.title(self.name)
		plt.show()

	def trim(self,wl1,wl2):
		w_arr = np.array([wl1,wl2])
		if wl1>wl2:
			w_arr = np.flipud(w_arr)
		new_ocd_spec = ocd_spec()
		idx1, = np.where(self.wl == wl1)
		idx2, = np.where(self.wl == wl2)
		new_wl = self.wl[int(idx1):int(idx2)+1]
		new_ocd_spec.wl = new_wl
		new_ocd_spec.cd = self.cd[int(idx1):int(idx2)+1]
		new_ocd_spec.dw = self.dw
		new_ocd_spec.name = self.name +" ["+str(wl1)+":"+str(wl2)+"]"
		return new_ocd_spec

	def rm_baseline(self,constant,type="constant",plot=False):
		new_ocd_spec = ocd_spec()
		baseline = constant*np.ones(len(self.wl))
		new_ocd_spec.cd = self.cd - baseline
		new_ocd_spec.wl = self.wl
		new_ocd_spec.name = self.name +" [Baseline Corrected]"
		new_ocd_spec.dw = self.dw
		if plot != False:
			fig = plt.figure("Baseline Correction")
			plt.plot(self.wl,self.cd,'k:')
			plt.plot(new_ocd_spec.wl,new_ocd_spec.cd,'k')
			plt.plot(self.wl,np.zeros(len(self.wl)),'k:')
			plt.title("Baseline Correction")
			plt.ylabel("CD [mdeg]")
			plt.xlabel("Wavelength [nm]")
			plt.legend([self.name,new_ocd_spec.name],loc='best')
			plt.show()
		return new_ocd_spec

	def filter(self,type="kaiser",beta=2.0,plot=True):
		new_ocd_spec = ocd_spec()
		new_ocd_spec.name = self.name + "[Filtered]"
		new_ocd_spec.wl = self.wl
		new_ocd_spec.dw = self.dw
		new_ocd_spec.cd = kaiser_smooth(self.cd,1)
		fig = plt.figure("Filtered Signal")
		plt.title("Filtered Signal")
		plt.ylabel("CD [mdeg]")
		plt.xlabel("Wavelength [nm]")
		plt.plot(self.wl,self.cd,color='salmon',linewidth=4)
		plt.plot(new_ocd_spec.wl,new_ocd_spec.cd,'k')
		plt.plot(self.wl,np.zeros(len(self.wl)),'k:')
		plt.legend([self.name,new_ocd_spec.name],loc='best')
		axis_y = np.zeros(len(self.wl))
		plt.plot(self.wl,axis_y,'k:')
		plt.show()			
		return new_ocd_spec

def load_files(filelist):
	names = []
	speclist = []
	for i in range(len(filelist)):
		print("(Formal) name of scan "+str(i+1))
		name = input()
		names.append(name)
	for i in range(len(filelist)):
		speclist.append(ocd_spec(filelist[i]))
		speclist[i].name = names[i]
	return speclist	
	
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
	avg.dw = specs[0].dw
	return avg 

def mult_graph(specs,types=None,colors=None,widths=None,title=None,verts=None):
	fig = plt.figure("Composite Plot")
	axis_y = np.zeros(len(specs[0].wl))
	plt.title(title)
	plt.xlabel("Wavelength [nm]")
	plt.ylabel("CD [mdeg]")
	if types != None and colors == None:
		names=[]
		for i,j in zip(specs,types):
			plt.plot(i.wl,i.cd,j)
			names.append(i.name)
		plt.legend(names,loc="best")
	if types != None and colors != None:
		names=[]
		for i,j,k in zip(specs,types,colors):
			plt.plot(i.wl,i.cd,j,color=k)
			names.append(i.name)
		plt.legend(names,loc="best")
	if types == None and colors == None:
		names=[]
		for i in specs:
			plt.plot(i.wl,i.cd)
			names.append(i.name)
		plt.legend(names,loc="best")
	if verts != None:
		for i in range(len(verts)):
			plt.axvline(x=verts[i])
	plt.plot(specs[0].wl,axis_y,'k:')
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
	try:
		from fileclaw import *
	except:
		print("Fileclaw module not found.")


	
