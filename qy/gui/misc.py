import wx

class timeBinSlider(wx.Panel):
    ''' A GUI slider '''
    def __init__(self, parent, label, default_value=0, max_value=200):
        ''' Constructor '''
        self.label=label
        wx.Panel.__init__(self, parent)
        sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.slider=wx.Slider(self, value=0, minValue=0, maxValue=max_value, size=(200,20))
        self.slider.SetLineSize(1)
        sizer.Add(self.slider, 1, wx.EXPAND)
        self.slider.Bind(wx.EVT_SCROLL, self.update)
        self.indicator=wx.StaticText(self, label='')
        self.indicator.SetMinSize((130, 20))
        sizer.Add(self.indicator, 0, wx.LEFT, 10)
        self.SetValue(default_value)
        self.SetSizerAndFit(sizer)

    def SetValue(self, n):
        ''' Set the value indicated '''
        self.slider.SetValue(n)
        self.update()

    def GetValue(self):
        ''' Get the current delay '''
        return self.slider.GetValue()

    def update(self, event=None):
        ''' Update the GUI components '''
        tb=int(self.slider.GetValue())
        ns=tb*0.082305
        if len(self.label)>0:
            s='%s = %d tb (%.2f ns)' % (self.label, tb, ns)
        else:
            s='%d tb (%.2f ns)' % (tb, ns)
        self.indicator.SetLabel(s)
        self.indicator.Fit()

