import colors
from Tkinter import *

class pilgraph(Frame):
	def __init__(self, parent, **options):
		Frame.__init__(self, parent, **options)
		self.canvas=Canvas(self, bg='#ffffff')
		self.canvas.pack(fill=BOTH, expand=1)
		self.cursor=0
		self.curves=[[]]
				
	def clear(self):
		print 'CLEAR'
		self.height=self.canvas.winfo_height()
		self.width=self.canvas.winfo_width()
		self.canvas.delete('all')
		
	def draw_curves(self, curves):
		self.cursor=0
		self.curves=curves.values()
		
	def tick(self):
		if self.cursor>len(self.curves[0])-2: return
		if self.curves==None: return
		curves=self.curves
		
		for i in range(len(curves)):
			curve=curves[i]
			if curve==[]: return
			color=colors.get_color(i)
			mx=max(1, float(max(curve)))
			curve=map(lambda x: self.height-0.9*self.height*x/mx, curve)
			q=range(len(curve))
			q=map(lambda x: self.width*x/len(curve), q)
			xy=zip(q, curve)
			q=xy[self.cursor:self.cursor+2]
			if len(q)<2: return
			self.canvas.create_line(q, fill=color, width=2)
		self.cursor+=1
	
		
		