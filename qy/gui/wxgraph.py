import wx
import qy.graphics
import matplotlib
matplotlib.interactive(False)
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import numpy as np

HISTORY_SIZE=100

class curve:
    def __init__(self, pattern, index, axes):
        ''' An object representing a curve '''
        self.pattern=pattern
        self.index=index
        self.alive=True
        self.color=qy.graphics.colors.get_color(index)
        self.xdata=np.arange(HISTORY_SIZE)
        self.ydata=np.ones([HISTORY_SIZE])*-1
        self.plot_curve=axes.plot([], [], color=self.color, lw=2, linestyle='-')[0]
        self.max_line=axes.plot([], [], color=self.color, lw=.5, linestyle=':')[0]


    def add_point(self, value):
        ''' Add a point to the curve and wrap around when we run out of history '''
        self.ydata=np.append(self.ydata, value)
        if len(self.ydata)>HISTORY_SIZE:
            self.ydata=self.ydata[1:]


    def update(self):
        ''' Draw the curve '''
        mask=self.ydata>=0
        self.plot_curve.set_xdata(self.xdata[mask])
        self.plot_curve.set_ydata(self.ydata[mask])
        self.max_line.set_xdata([0, HISTORY_SIZE])
        self.max_line.set_ydata([max(self.ydata)]*2)
        if sum(mask)==0:
            self.alive=False
            self.plot_curve.remove()
            self.max_line.remove()


class graph_panel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)
        self.curves={}
        self.beep=qy.settings.get('realtime.sound')
        self.hi_contrast=False
        self.build()


    def build(self):
        ''' build the whole thing '''
        # Set up the graph
        self.fig = Figure(dpi=110)
        self.fig.set_facecolor('#000000')
        self.canvas = FigCanvas(self, -1, self.fig)
        self.axes1=self.add_axes(211)
        self.axes2=self.add_axes(212)
        self.fig.subplots_adjust(left=.08, right=.97, top=.96, bottom=.08)

        # Configure wx
        self.Bind(wx.EVT_SIZE, self.sizeHandler)
        self.SetMinSize((400,200))


    def add_axes(self, subplot_index):
        ''' Prepare a new set of axes '''
        ax=self.fig.add_subplot(subplot_index)
        ax.set_axis_bgcolor('#000000')
        ax.set_xlim(0, HISTORY_SIZE)
        yfm=ax.yaxis.get_major_formatter()
        yfm.set_powerlimits([0,1])
        for s in ['top', 'bottom', 'right', 'left']:
            ax.spines[s].set_color('white')

        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.get_offset_text().set_color('white')
        return ax


    def toggle_hi_contrast(self, event):
        ''' Toggle hi-contrast mode '''
        hi_contrast = event.GetEventObject().IsChecked()
        for key, curve in self.curves.items():
            curve.plot_curve.set_color('white' if hi_contrast else curve.color)
            curve.max_line.set_color('white' if hi_contrast else curve.color)


    def draw(self):
        ''' Draw/update all of the curves '''
        # Update the curves
        for c in self.curves.values():
            c.update()

        # Rescale the axes
        for ax in [self.axes1, self.axes2]:
            ax.relim()
            ax.autoscale_view(False,True,True)

        # Draw to the canvas
        self.canvas.draw()


    def sizeHandler(self, *args, **kwargs):
        ''' Makes sure that the canvas is properly resized '''
        self.canvas.SetSize(self.GetSize())


    def add_counts(self, data):
        ''' Add a set of counts '''
        # Process the data, and generate new curves if appropriate
        curves_done=set()
        for item in data:
            pattern=item['pattern']
            if not pattern in self.curves:
                axis=self.axes1 if len(pattern)==1 else self.axes2
                self.curves[pattern]=curve(pattern, item['index'], axis)
            curves_done.add(pattern)
            self.curves[pattern].add_point(item['count'])

        # Check the curves which were not updated
        difference=set(self.curves.keys()).difference(curves_done)
        for key in difference:
            self.curves[key].add_point(-1)

        # Cull dead curves
        for key in self.curves.keys():
            if self.curves[key].alive==False: del self.curves[key]

        # Redraw the graph!
        self.draw()


