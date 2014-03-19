import os, time
import wx
from qy import settings
from multiprocessing import Process, Pipe
import wxgraph, wxbrowser

class photon_elf(wx.Frame):
    ''' A simple GUI to talk to counting systems '''
    def __init__(self, pipe=None):
        ''' Constructor '''
        # Figure out where we should send/recieve data
        self.send = (lambda x: x) if pipe==None else pipe.send
        self.recv = (lambda x: x) if pipe==None else pipe.recv

        # Start building
        self.app = wx.App(False)
        self.build()
        self.load_defaults()
        self.app.MainLoop()


    def build(self):
        ''' Builds the various pieces of the GUI ''' 
        wx.Frame.__init__(self, None, title='PHOTON ELF', size=(500,100))
        self.Bind(wx.EVT_CLOSE, self.quit)

        # Build both panels
        self.graph=wxgraph.graph_panel(self)
        self.build_left_panel()
        
        # The main sizer
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainsizer.Add(self.left_panel, 0, wx.ALL|wx.EXPAND, 5)
        self.mainsizer.Add(self.graph, 1, wx.EXPAND)
        
        # Put things together
        self.SetSizerAndFit(self.mainsizer)
        self.Show()
        self.SetMinSize((400,300))
        self.SetSize((700,500))

        
    def build_left_panel(self):
        ''' Build the left panel '''
        # Prepare the panel
        self.left_panel_sizer=wx.BoxSizer(wx.VERTICAL)
        self.left_panel=wx.Panel(self)
        self.left_panel.SetSizer(self.left_panel_sizer)
        self.left_panel.SetMinSize((200, 100))

        # Status boxes
        self.status=wx.StaticText(self.left_panel, label='DPC230 status', style=wx.ST_NO_AUTORESIZE)
        self.status.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.left_panel_sizer.Add(self.status, 0, wx.EXPAND|wx.TOP, 5)

        # Browser
        self.browser=wxbrowser.browser(self.left_panel)
        self.browser.bind_change(self.graph.clear)
        self.left_panel_sizer.Add(self.browser, 0, wx.EXPAND|wx.ALL)
        
        # Graph configuration
        #graph_config_sizer=wx.BoxSizer(wx.HORIZONTAL)
        #graph_config_sizer.Add((0,0), 1)
        #self.left_panel_sizer.Add(graph_config_sizer, 0, wx.BOTTOM, 8)


    def quit(self, *args):
        ''' Close down gracefully, and then destroy the window '''
        self.save_defaults()
        self.send(('gui_quit', None))
        self.Destroy()


    def load_defaults(self):
        ''' Load the most recently used settings '''
        patterns=settings.get('realtime.browser_searches')
        self.browser.set_patterns(patterns)
        

    def save_defaults(self):
        ''' Save the settings for next time '''
        settings.put('realtime.browser_searches', self.browser.get_patterns())


class threaded_gui:
    ''' A multithreaded handler for the coincidence-count GUI '''
    def __init__(self):
        ''' Constructor '''
        # Start up the GUI process and build the communication network
        self.pipe, their_pipe = Pipe()
        self.gui = Process(target=photon_elf, name='photon_elf', args=(their_pipe,))
        self.gui.start()

    def send(self, message):
        ''' Send a message asynchrously to the GUI '''
        self.pipe.send(message)

    def recv(self, timeout=1):
        ''' Try to get a message from the GUI, else timeout '''
        if self.pipe.poll(timeout):
            return self.pipe.recv()


if __name__=='__main__':
    main=threaded_gui()
    while True:
        out=main.recv()
        if out:
            print out









