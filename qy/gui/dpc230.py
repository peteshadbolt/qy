import wx
import coincidence_counting
import wxbrowser
from multiprocessing import Process, Pipe
import qy.settings
import qy.util
import misc

class dpc230_settings(wx.Dialog):
    def __init__(self, parent, callback=None):
        ''' A dialog to control the delays '''
        self.callback = (lambda x: x) if callback==None else callback
        self.build(parent)

    def simple_label(self, label):
        ''' Add a simple bit of text '''
        label=wx.StaticText(self, label=label, style=0)
        label.SetFont(wx.Font(10, wx.NORMAL, wx.NORMAL, wx.BOLD))
        self.mainsizer.Add(label, 1, wx.TOP, 10)

    def build(self, parent):
        ''' Construct the body of the GUI '''
        wx.Dialog.__init__(self, parent, title='DPC230 Options', size=(350,300))
        self.mainsizer=wx.BoxSizer(wx.VERTICAL)

        # Make the coincidence window
        self.simple_label('Coincidence window')
        default = qy.settings.get('dpc230.coincidence_window')
        self.coincidence_window = misc.timeBinSlider(self, '', default)
        self.mainsizer.Add(self.coincidence_window, 0, wx.ALL, 2)

        # Make the delay lines
        self.simple_label('Delays')
        defaults = qy.settings.get('dpc230.delays')
        self.delay_lines=[]
        for i in range(len(defaults)):
            d=misc.timeBinSlider(self, qy.util.alphabet_upper[i], defaults[i])
            self.delay_lines.append(d)
            self.mainsizer.Add(d, 0, wx.EXPAND|wx.ALL, 2)

        # Finish up
        self.SetSizerAndFit(self.mainsizer)

        # Set up the timer
        timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, timer)
        timer.Start(1000)


    def ontimer(self, event):
        ''' Every timer event, send the delays '''
        delays=[q.GetValue() for q in self.delay_lines]
        self.callback(['delays', delays])


class gui_head(coincidence_counting.gui_head):
    ''' A simple GUI for the DPC230 '''
    def __init__(self, pipe=None):
        ''' Constructor. Inherits from coincidence_counting '''
        coincidence_counting.gui_head.__init__(self, pipe)

    def show_settings(self, arg):
        ''' Show the delay dialog '''
        dialog=dpc230_settings(parent=self, callback=None)
        dialog.ShowModal()
        #dialog.Destroy()

    def populate_left_panel(self):
        ''' Build the left panel '''
        # Status box
        self.status=wx.StaticText(self.left_panel, label='DPC230', style=wx.ST_NO_AUTORESIZE|wx.SUNKEN_BORDER)
        self.status.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.left_panel_sizer.Add(self.status, 0, wx.EXPAND|wx.BOTTOM, 5)

        # Button
        self.configure_button=wx.Button(self.left_panel, label='Options')
        self.configure_button.Bind(wx.EVT_BUTTON, self.show_settings)
        self.left_panel_sizer.Add(self.configure_button, 0, wx.EXPAND|wx.BOTTOM, 5)

        # Browser
        self.browser=wxbrowser.browser(self.left_panel)
        self.left_panel_sizer.Add(self.browser, 0, wx.EXPAND|wx.ALL)


class gui(coincidence_counting.gui):
    ''' A Multithreaded handler for the DPC230 GUI '''
    def __init__(self):
        ''' Constructor. Inherits from coincidence_counting '''

        # Start up the GUI process and build the communication network
        self.pipe, their_pipe = Pipe()
        self.gui = Process(target=gui_head, name='gui_head', args=(their_pipe,))
        self.gui.start()


if __name__=='__main__':
    g=gui()
