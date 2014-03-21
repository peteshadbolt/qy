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

    def on_close(self, arg):
        ''' Is called when the dialog is closed '''
        delays=[q.GetValue() for q in self.delay_lines]
        window=self.coincidence_window.GetValue()
        integration_time=self.integration_time.GetValue()
        qy.settings.put('dpc230.delays', delays)
        qy.settings.put('dpc230.coincidence_window', window)
        qy.settings.put('realtime.integration_time', integration_time)
        self.timer.Stop()
        self.Destroy()

    def simple_label(self, label):
        ''' Add a simple bit of text '''
        label=wx.StaticText(self, label=label, style=0)
        label.SetFont(wx.Font(10, wx.NORMAL, wx.NORMAL, wx.BOLD))
        self.mainsizer.Add(label, 1, wx.TOP, 10)

    def build(self, parent):
        ''' Construct the body of the GUI '''
        wx.Dialog.__init__(self, parent, title='DPC230 Options', size=(350,300))
        self.mainsizer=wx.BoxSizer(wx.VERTICAL)

        # Make the integration time 
        self.simple_label('Integration time')
        default = qy.settings.get('realtime.integration_time')
        self.integration_time = misc.integrationSlider(self, default)
        self.mainsizer.Add(self.integration_time, 0, wx.ALL, 2)

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
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Set up the timer
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
        self.timer.Start(1000)


    def ontimer(self, event):
        ''' Every timer event, send the delays '''
        delays=[q.GetValue() for q in self.delay_lines]
        window=self.coincidence_window.GetValue()
        integration_time=self.integration_time.GetValue()
        self.callback(['delays', delays])
        self.callback(['coincidence_window', window])
        self.callback(['integration_time', integration_time])


class gui_head(coincidence_counting.gui_head):
    ''' A simple GUI for the DPC230 '''
    def __init__(self, pipe=None):
        ''' Constructor. Inherits from coincidence_counting '''
        coincidence_counting.gui_head.__init__(self, pipe)


    def show_settings(self, arg):
        ''' Show the delay dialog '''
        dialog=dpc230_settings(parent=self, callback=self.send)
        dialog.Show()

    def save_defaults(self):
        ''' Save the settings for next time '''
        coincidence_counting.gui_head.save_defaults(self)
        qy.settings.put('realtime.sound', self.beep.GetValue())


    def populate_left_panel(self):
        ''' Build the left panel '''
        # Status box
        self.status=wx.StaticText(self.left_panel, label='DPC230', style=wx.ST_NO_AUTORESIZE)
        self.status.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        self.left_panel_sizer.Add(self.status, 0, wx.EXPAND|wx.BOTTOM, 5)

        # Various options!
        self.hi_contrast = wx.CheckBox(self.left_panel, label='Goggles')
        self.left_panel_sizer.Add(self.hi_contrast, 0, wx.BOTTOM, 5)
        self.hi_contrast.Bind(wx.EVT_CHECKBOX, self.graph.toggle_hi_contrast)
        self.beep = wx.CheckBox(self.left_panel, label='Sound')
        self.beep.SetValue(qy.settings.get('realtime.sound'))
        self.left_panel_sizer.Add(self.beep, 0, wx.BOTTOM, 5)

        # Button
        self.configure_button=wx.Button(self.left_panel, label='Options')
        self.configure_button.Bind(wx.EVT_BUTTON, self.show_settings)
        self.left_panel_sizer.Add(self.configure_button, 0, wx.EXPAND|wx.BOTTOM, 5)

        # Browser
        self.browser=wxbrowser.browser(self.left_panel)
        self.left_panel_sizer.Add(self.browser, 0, wx.EXPAND|wx.ALL)
        self.beep.Bind(wx.EVT_CHECKBOX, self.browser.toggle_beep)


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
