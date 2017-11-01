from curses import *
import numpy as np
import matplotlib as mpl


class ocd_spec:
	def renorm(self,scale_factor):
		self.cd = scale_factor*self.cd	

	def load(self,fn):
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
		
	def __radd__(self,other):
		if other == 0:
			return self
		else:
			return self.__add__(other)

	def __init__(self,fn=None):
		if fn is not None:
			self.data = self.load(fn)
			self.wl = np.flipud(np.array(self.data[:,0]))
			self.cd = np.flipud(np.array(self.data[:,1]))
		if fn is None:
			self.data = np.array([[]])
			self.wl = np.array([])
			self.cd = np.array([])

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


