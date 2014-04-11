import wx
from multiprocessing import Process, Pipe
import qy.settings
import qy.util
import misc

class gui_head(wx.Frame):
    ''' A simple GUI to talk to the SMC100 '''
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

        # Periodically check for messages
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
        self.timer.Start(100)
        self.app.MainLoop()


    def handle_input(self, key, value):
        ''' Update the status box '''
        if key=='status':
            s=self.status.GetLabel()
            self.status.SetLabel(value+'\n'+s[:1000])
        elif key=='kill':
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
        wx.Frame.__init__(self, None, title='SMC100 Motor Controller', size=(500,100))
        self.Bind(wx.EVT_CLOSE, self.quit)
        self.SetBackgroundColour((220,220,220))

        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        self.status=wx.StaticText(self, label='Booting SMC100...', style=wx.ST_NO_AUTORESIZE)
        self.status.SetBackgroundColour((30,30,30))
        self.status.SetForegroundColour((255,255,255))
        self.status.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.mainsizer.Add(self.status, 1, wx.EXPAND)

        self.Show()
        self.SetMinSize((400,300))
        self.SetSize((700,500))


    def quit(self, *args):
        ''' Close down gracefully, and then destroy the window '''
        self.send(('gui_quit', None))
        self.Destroy()

        



class gui:
    ''' A multithreaded handler for the SMC100 GUI '''
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


if __name__=='__main__':
    g=gui()
