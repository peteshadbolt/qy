import os, time
import wx
from qy import settings
from multiprocessing import Process, Pipe
import wxgraph, wxbrowser

class gui_head(wx.Frame):
    ''' A simple GUI to talk to counting systems '''
    def __init__(self, pipe=None):
        ''' Constructor '''
        # Figure out where we should send/recieve data
        self.pipe=pipe
        self.poll = None if pipe==None else pipe.poll
        self.send = (lambda x: x) if pipe==None else pipe.send
        self.recv = (lambda x: x) if pipe==None else pipe.recv

        # Build the interface
        self.app = wx.App(False)
        self.build()
        self.load_defaults()

        # Periodically check for messages
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
        self.timer.Start(100)
        self.app.MainLoop()

    def handle_input(self, key, value):
        ''' Handle a key/value pair '''
        if key=='status':
            self.status.SetLabel(value)
        elif key=='count_rates':
            filtered_counts=self.browser.update_count_rates(value)
            self.graph.add_counts(filtered_counts)
        elif key=='shutdown':
            self.quit()

    def ontimer(self, arg):
        ''' This function is called four times per second '''
        # Look for messages coming down the pipe
        while self.pipe.poll():
            key, value=self.recv()
            self.handle_input(key, value)
        self.Update()

    def build(self):
        ''' Builds the various pieces of the GUI '''
        wx.Frame.__init__(self, None, title='PHOTON ELF', size=(500,100))
        self.Bind(wx.EVT_CLOSE, self.quit)
        self.SetBackgroundColour((220,220,220))

        # Build both panels
        self.graph=wxgraph.graph_panel(self)
        self.left_panel_sizer=wx.BoxSizer(wx.VERTICAL)
        self.left_panel=wx.Panel(self)
        self.left_panel.SetDoubleBuffered(True)
        self.left_panel.SetSizer(self.left_panel_sizer)
        self.left_panel.SetMinSize((250, 100))
        self.populate_left_panel()

        # The main sizer
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainsizer.Add(self.left_panel, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.graph, 1, wx.EXPAND)

        # Put things together
        self.SetSizerAndFit(self.mainsizer)
        self.Show()
        self.SetMinSize((400,300))
        self.SetSize((700,500))


    def populate_left_panel(self):
        ''' Populate the left panel '''
        # Status boxes
        self.status=wx.StaticText(self.left_panel, label='PHOTON ELF', style=wx.ST_NO_AUTORESIZE)
        self.status.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.left_panel_sizer.Add(self.status, 0, wx.EXPAND|wx.TOP, 5)

        # Browser
        self.browser=wxbrowser.browser(self.left_panel)
        self.left_panel_sizer.Add(self.browser, 0, wx.EXPAND|wx.ALL)


    def quit(self, *args):
        ''' Close down gracefully, and then destroy the window '''
        self.save_defaults()
        self.send(('gui_quit', None))
        self.Destroy()


    def load_defaults(self):
        ''' Load the most recently used settings '''
        patterns=settings.get('realtime.patterns')
        self.browser.set_patterns(patterns)


    def save_defaults(self):
        ''' Save the settings for next time '''
        settings.put('realtime.patterns', self.browser.get_patterns())


class gui:
    ''' A multithreaded handler for the coincidence-count GUI '''
    def __init__(self):
        ''' Constructor '''
        # Start up the GUI process and build the communication network
        self.pipe, their_pipe = Pipe()
        self.gui = Process(target=gui_head, name='gui_head', args=(their_pipe,))
        self.gui.start()

    def collect(self):
        ''' Collect all messages and act upon them '''
        messages=[]
        while self.pipe.poll(0):
            messages.append(self.pipe.recv())
        return messages

    def send(self, key, value):
        ''' Send a message to the threaded GUI '''
        self.pipe.send((key, value))












