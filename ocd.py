# -*- coding: utf-8 -*-
'''
 ┌┬──────────────────────────────────┬┐
 └┤   OCD ANALYSIS SOFTWARE          ├┘
 ┌┤   Nick Charron - Huang Lab       ├┐
 └┤   Rice Univ - 2017               ├┘
 ┌┤   charron.nicholas.e@gmail.com   ├┐
 └┴──────────────────────────────────┴┘
'''
import sys
import os
import numpy as np
import matplotlib as mpl
if sys.platform == 'darwin':
	mpl.use('TkAgg')
import matplotlib.pyplot as plt

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
		new_ocd_spec = ocd_spec()
		new_ocd_spec.wl = self.wl
		new_ocd_spec.dw = self.dw
		new_ocd_spec.name = self.name + "[Rescaled]"
		new_ocd_spec.cd = scale_factor*self.cd
		return new_ocd_spec

	def load(self,fn):
		'''Specific to J810 ASCII'''
		data = np.loadtxt(fn,dtype=float,skiprows=19,usecols=(0,1))
		return data

	def save(self,fn):
		'''For future loading'''
		savefile = open(fn,"w+")
		savefile.write(self.name+"\n")
		'''Mimic JASCO Header'''
		for i in range(18):
			savefile.write("* * * * * * * * * *\n")
		'''Write wl and cd values'''
		for i in range(len(self.wl)):
			savefile.write("{}\t{}\n".format(self.wl[i],self.cd[i]))
		savefile.close()

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

	def filter(self,type="kaiser",beta=2.0,plot=True,lwidths=[1,1]):
		new_ocd_spec = ocd_spec()
		new_ocd_spec.name = self.name + "[Filtered]"
		new_ocd_spec.wl = self.wl
		new_ocd_spec.dw = self.dw
		new_ocd_spec.cd = kaiser_smooth(self.cd,1)
		fig = plt.figure("Filtered Signal")
		plt.title("Filtered Signal")
		plt.ylabel("CD [mdeg]")
		plt.xlabel("Wavelength [nm]")
		plt.plot(self.wl,self.cd,color='salmon',linewidth=lwidths[1])
		plt.plot(new_ocd_spec.wl,new_ocd_spec.cd,'k',linewidth=lwidths[0])
		plt.plot(self.wl,np.zeros(len(self.wl)),'k:')
		plt.legend([self.name,new_ocd_spec.name],loc='best')
		axis_y = np.zeros(len(self.wl))
		plt.plot(self.wl,axis_y,'k:')
		plt.show()			
		return new_ocd_spec
			
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

def mult_graph(specs,types=None,colors=None,lwidths=None,title=None,verts=None,xlim=None):
	if lwidths == None:
		lwidths = [1]*len(specs)
	fig = plt.figure("Composite Plot")
	axis_y = np.zeros(len(specs[0].wl))
	plt.title(title)
	plt.xlabel("Wavelength [nm]")
	plt.ylabel("CD [mdeg]")
	if types != None and colors == None:
		names=[]
		for i,j,k in zip(specs,types,lwidths):
			plt.plot(i.wl,i.cd,j,linewidth=k)
			names.append(i.name)
		plt.legend(names,loc="best")
	if types != None and colors != None:
		names=[]
		for i,j,k,l in zip(specs,types,colors,lwidths):
			plt.plot(i.wl,i.cd,j,color=k,linewidth=k)
			names.append(i.name)
		plt.legend(names,loc="best")
	if types == None and colors == None:
		names=[]
		for i in range(len(specs)):
			plt.plot(specs[i].wl,specs[i].cd,linewidth=lwidths[i])
			names.append(specs[i].name)
		plt.legend(names,loc="best")
	if verts != None:
		for i in range(len(verts)):
			plt.axvline(x=verts[i])
	plt.plot(specs[0].wl,axis_y,'k:')
	if xlim != None and len(xlim) == 2:
		plt.xlim(xlim[0],xlim[1])
	plt.show()	
		
def graph_series(specs,title=None,cmap=mpl.cm.Reds,lwidths=None,xlim=None):
	if lwidths == None:
		lwidths = [1]*len(specs)
	fig = plt.figure("Series Plot")
	plt.title(title)
	plt.xlabel("Wavelength [nm]")
	plt.ylabel("CD [mdeg]")
	names=[]
	for i in range(len(specs)):
		plt.plot(specs[i].wl,specs[i].cd,color=cmap((i+1)*1./len(specs)), linewidth=lwidths[i])
		names.append(specs[i].name)
	plt.legend(names,loc="best")
	if xlim != None and len(xlim) == 2:
		plt.xlim(xlim[0],xlim[1])
	plt.show()

if sys.platform == "win32":
	try:
		import wx

		def fs():
			app = wx.App(None)
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
			dialog = wx.FileDialog(None, 'Open',wildcard='*.txt',style=style)
			mult = None
			if dialog.ShowModal() == wx.ID_OK:
				try:
					paths = dialog.GetPath()
					mult = False
				except:
					paths = dialog.GetPaths()
					mult = True
			else:
				paths = None
			dialog.Destroy()
			if mult == False:
				return ocd_spec(paths[0])
			if mult == True:
				specs =[]
				for i in paths:
					specs.append(ocd_spec(i))
				return specs

		def mfs():
			app = wx.App(None)
			style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
			dialog = wx.FileDialog(None,'Open',wildcard='*.txt',style=style)
			if dialog.ShowModal() == wx.ID_OK:
				paths = dialog.GetPaths()
			else:
				paths =None
			dialog.Destroy()
			specs = []
			for i in paths:
				specs.append(ocd_spec(i))
			return specs

	except:
		print("WX module not found. Defaulting to CLI.")
	
if sys.platform == "linux" or sys.platform == "darwin" \
or sys.platform == "linux2":
	try:
		from dialog import Dialog
		dlg = Dialog(dialog="dialog")
		rows, cols = os.popen("stty size","r").read().split()
		rows = int(rows); cols = int(cols)
		
		def fs():
			path = './'
			entries = os.listdir(path)
			tagtuples = []
			for i in entries:
				tagtuples.append((i,i,"off"))
			code, paths = dlg.buildlist("Select Files",rows-10,cols-10,rows-14,tagtuples)
			if code == Dialog.OK:
				if len(paths) == 1:
					return ocd_spec(paths[0])
				else:	
					specs=[]
					for i in paths:
						specs.append(ocd_spec(i))
					return specs
			if code == Dialog.CANCEL:
				return None
	except:
		print("Dialog module not found. Defaulting to CLI.")
		
