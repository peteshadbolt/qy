import wx
import qy
import qy.graphics
import matplotlib
matplotlib.interactive(False)
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
#matplotlib.rc('font', family='arial', size=10)
#matplotlib.use('WXAgg')

import numpy as np

class curve:
    def __init__(self, index, label, axes, history_size=50):
        ''' an object representing a curve '''
        self.label=label
        self.index=index
        self.color=qy.graphics.colors.get_color(index)
        self.xdata=np.arange(history_size)
        self.ydata=np.array([])
        self.history_size=history_size
        self.plot_curve=axes.plot([], [], color=self.color, lw=1, linestyle='-')[0]
        self.max_line=axes.plot([], [], color=self.color, lw=1, linestyle='--', alpha=.5)[0]
        
    def add_point(self, value):
        ''' add a point to the curve and wrap around when we run out of history '''
        self.ydata=np.append(self.ydata, value)
        if len(self.ydata)>self.history_size:
            self.ydata=self.ydata[1:]
        
    def update(self):
        ''' draw the curve '''
        self.plot_curve.set_xdata(self.xdata[:len(self.ydata)])
        self.plot_curve.set_ydata(self.ydata)
        
        self.max_line.set_xdata([0, self.history_size])
        mx=max(self.ydata)
        self.max_line.set_ydata([mx, mx])


class graph_panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.previous_patterns=[]
        self.history_size=100
        self.hi_contrast=False
        self.big_numbers=False
        self.need_data=True
        self.build()
        
    def build(self):
        ''' build the whole thing '''
        self.fig = Figure(dpi=110)
        self.fig.set_facecolor('#000000')
        self.canvas = FigCanvas(self, -1, self.fig)
        self.Bind(wx.EVT_SIZE, self.sizeHandler)
        self.SetMinSize((400,200))
        self.buildgraph()
        
    def add_axes(self, subplot_index):
        ''' add a new set of axes '''
        ax=self.fig.add_subplot(subplot_index)
        ax.set_axis_bgcolor('#000000')
        ax.set_xlim(0, self.history_size)
        #ax.set_yscale('log', nonposx='clip')
        #ax.set_ylim(ymin=0)
        yfm=ax.yaxis.get_major_formatter()
        yfm.set_powerlimits([0,1])
        ax.spines['top'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.get_offset_text().set_color('white')
        return ax
        
    def add_big_text(self, ax):
        ''' add big text '''
        text=ax.text(0.01, 0.95, '', transform=ax.transAxes, color='#ffffff', va='top', fontsize=45)
        return text
                        
    def buildgraph(self):
        ''' build the graph bits '''
        self.fig.clf()
        self.axes1=self.add_axes(211)
        self.axes2=self.add_axes(212)
        self.fig.subplots_adjust(left=.08, right=.97, top=.96, bottom=.08)
        
    def sizeHandler(self, *args, **kwargs):
        ''' makes sure that the canvas is properly resized '''
        self.canvas.SetSize(self.GetSize())
    
    def set_hi_contrast(self, event):
        ''' set the contrast '''
        self.hi_contrast=event.IsChecked()
        for c in self.all_curves:
            if self.hi_contrast:
                c.plot_curve.set_lw(1)
                c.plot_curve.set_color('white')
            else:
                c.plot_curve.set_lw(1)
                c.plot_curve.set_color(c.color)
        
    def set_big_numbers(self, event):
        ''' set the contrast '''
        self.big_numbers=event.IsChecked()
                    
    def clear(self):
        ''' called when the pattern changes '''
        if self.need_data==False:
            self.buildgraph()
        self.need_data=True
        self.singles_curves=[]
        
    def add_counts(self, data):
        ''' add a set of counts '''
        new_singles=filter(lambda x: len(x[1])==1, data)
        new_coincidences=filter(lambda x: len(x[1])>1, data)
        
        if self.need_data:
            self.singles_curves=[curve(q[0], q[1], self.axes1, self.history_size) for q in new_singles]
            self.coincidence_curves=[curve(q[0], q[1], self.axes2, self.history_size) for q in new_coincidences]
            self.all_curves=self.singles_curves+self.coincidence_curves
            self.need_data=False
            
        for i in range(len(self.singles_curves)):
            self.singles_curves[i].add_point(new_singles[i][2])

        for i in range(len(self.coincidence_curves)):
            self.coincidence_curves[i].add_point(new_coincidences[i][2])
            
        self.draw()
        
    def get_big_number_text(self, curve_group):
        ''' update the big number text '''
        text=''
        for c in curve_group:
            s=format(int(c.ydata[-1]), ',d')
            s='%s: %s\n' % (c.label, s)
            text+=s
        return text
        
    def rescale_axes(self):
        ''' rescale all the axes '''
        self.axes1.relim()
        self.axes1.autoscale_view(True,True,True)
        self.axes2.relim()
        self.axes2.autoscale_view(True,True,True)

    def draw(self):
        ''' draw all of the curves etc '''
        for c in self.all_curves:
            c.update()
        
        self.rescale_axes()
        self.canvas.draw()
