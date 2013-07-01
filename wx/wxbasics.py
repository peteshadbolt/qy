import wx

class output_box(wx.Panel):
	def __init__(self, parent, label='', border=False):
		''' a label box with an optional border '''
		style=wx.SIMPLE_BORDER if border else wx.NO_BORDER
		wx.Panel.__init__(self, parent, style=style)
		if border: self.SetBackgroundColour(wx.Colour(255,255,255))
		
		self.SetDoubleBuffered(True)
		
		sizer=wx.BoxSizer(wx.VERTICAL)
		self.text=wx.StaticText(self, label=label)
		
		sizer.Add((0,0), 1)
		bord=wx.RIGHT|wx.LEFT if border else wx.RIGHT
		sizer.Add(self.text, 0, bord, 8)
		sizer.Add((0,0), 1)
		sizer.SetMinSize((50, 25))
		self.SetSizerAndFit(sizer)
		
	def set_label(self, label):
		''' set the value of the label '''
		self.text.SetLabel(label)

class input_box(wx.Panel):
	def __init__(self, parent):
		''' an entry box which validates itself '''
		wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		sizer=wx.BoxSizer(wx.VERTICAL)
		self.text=wx.TextCtrl(self, style=wx.NO_BORDER)
		self.text.Bind(wx.EVT_TEXT, self.validate)
		self.indicate(True)
		
		sizer.Add((0,0), 1)
		sizer.Add(self.text, 0, wx.LEFT|wx.RIGHT|wx.TOP, 7)
		sizer.Add((0,0), 1)
			
		self.SetSizerAndFit(sizer)
		self.Layout()
		self.SetMinSize((70,25))
		
		# set up default values
		self.format=str
		self.limits=(None,None)
		self.previous_value=0
		
	def configure(self, format=str, limits=(None,None), initial_value=0):
		''' configure validation '''
		self.format=format
		self.limits=limits
		self.previous_value=initial_value
		self.text.ChangeValue(str(initial_value))
		
	def indicate(self, input_ok):
		col = wx.Colour(255,255,225) if input_ok else wx.Colour(255,200,200)
		self.SetBackgroundColour(col)
		self.text.SetBackgroundColour(col)
		self.Refresh()
		
	def validate(self, event=None):
		''' validate new input '''
		new_value=self.text.GetValue()
		self.indicate(False)
		
		try:
			new_value=self.format(new_value)
		except:
			return self.previous_value
			
		if self.limits[0] != None and new_value<self.limits[0]: return self.previous_value
		if self.limits[1] != None and new_value>self.limits[1]: return self.previous_value
		
		self.previous_value=new_value
		self.indicate(True)
		return new_value
		
	def get_value(self):
		''' get the value '''
		return self.validate()
		
class input_output_pair(wx.Panel):
	def __init__(self, parent, border=False, fill=False):
		''' a pair consisting of a label and an entry box '''
		wx.Panel.__init__(self, parent)
		sizer=wx.BoxSizer(wx.HORIZONTAL)

		self.label=output_box(self, '', border)
		self.entry=input_box(self)
		
		sizer.Add(self.label, 1, wx.RIGHT|wx.EXPAND, 2)
		sizer.Add(self.entry, 0, wx.EXPAND)
		
		self.SetSizerAndFit(sizer)
		
	def set_value(self, new_value):
		''' set the value of the input '''
		self.entry.text.SetValue(new_value)
		
	def bind_change(self, function):
		''' bind a function to the event where the text is changed '''
		self.entry.text.Bind(wx.EVT_TEXT, function)
					
	def configure(self, *args, **kwargs):
		''' configure the entry box '''
		self.entry.configure(*args, **kwargs)
			
	def set_label(self, label):
		''' set the value of the label '''
		self.label.set_label(label)
		
	def get_value(self):
		''' get the value of the entry box '''
		return self.entry.get_value()