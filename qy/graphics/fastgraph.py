import os
import colors
from Tkinter import *

class fastgraph:
	def __init__(self, canvas):
		# configure
		self.xpad_left=0
		self.xpad_right=5
		self.ypad=10.
		self.history_size=150
		self.hovered=False
		self.canvas=canvas
		self.width, self.height = 1000, 1000
		self.canvas.create_rectangle(0, 0, 1000, 1000, fill='#000000')
		
		self.canvas.bind('<Double-1>', lambda y: self.clear())
		self.canvas.bind('<Enter>', lambda y: self.enter())
		self.canvas.bind('<Leave>', lambda y: self.leave())
		
		# setup the history
		self.data=None
		
	def enter(self):
		self.hovered=True
		x, y = self.width/2, self.height/2
		self.canvas.create_text(x, y, text='Double-click to clear', fill='#666666', font='Arial 15', justify=CENTER)
	
	def leave(self):
		self.hovered=False
		
	def clear(self):
		self.canvas.delete('all')
		self.canvas.create_rectangle(0, 0, 1000, 1000, fill='#000000')
		self.data=None
			
	def add_counts(self, newdata, colors):
		if len(newdata)==0: return
		
		# if we don't already have data
		n=len(newdata)
		if self.data==None:
			self.data=[[] for i in range(n)]
			self.data_max=1
			self.data_min=100000000
		
		# add the new data
		self.colors=colors
		for i in range(n):
			self.data[i].append(newdata[i])
			if len(self.data[i])>self.history_size: del self.data[i][0]
		self.data_max=max(map(max, self.data))
		self.data_min=min(map(min, self.data))
		if self.data_max==self.data_min: self.data_max=self.data_min+1
		self.rescale_data()
		
	def redraw(self, data, colors, size, hi_contrast=False):
		if len(colors)==0: return 
		
		# check the contrast
		if hi_contrast:
			colors=['#222200' for c in colors]
			colors[0]='#ffffff'
		
		# load the data
		self.width, self.height = size
		self.size=size
		self.add_counts(data, colors)
		
		# clear the canvas and  draw all of the points
		self.canvas.delete('all')
		self.canvas.create_rectangle(0, 0, 1000, 1000, fill='#000000')
		
		if self.hovered:
			x, y = self.width/2, self.height/2
			self.canvas.create_text(x, y, text='Double-click to clear', fill='#666666', font='Arial 15', justify=CENTER)
		
		self.draw_data(hi_contrast)
		self.draw_axes()

	def scale_point(self, x, y):
		return int(self.xpad_left+x*self.x_scale), self.height-int((y-self.data_min)*self.y_scale)
		
	def rescale_data(self):
		N=len(self.data[0])
		if N<2: return
		self.x_scale=(self.width-self.xpad_left-self.xpad_right)/float(N)
		self.y_scale=(self.height-self.ypad)/float(self.data_max-self.data_min)
		self.scaled_data=[[self.scale_point(i, stream[i]) for i in range(N)] for stream in self.data]
	
	def draw_axes(self):
		self.canvas.create_text(10, 5, text=str(self.data_max), fill='#ffffff', font='Arial 15', anchor=NW, justify=LEFT)
		self.canvas.create_text(10, self.height-5, text=str(self.data_min), fill='#ffffff', font='Arial 15', anchor=SW, justify=LEFT)
		
	def draw_data(self, hi_contrast):
		if len(self.data[0])<2: return
		for i in range(len(self.data)):
			color=self.colors[i]
			width=5 if hi_contrast and i==0 else 1
			self.canvas.create_line(self.scaled_data[i], fill=color, width=width)