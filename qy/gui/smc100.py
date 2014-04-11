import wx
import coincidence_counting
import wxbrowser
from multiprocessing import Process, Pipe
import qy.settings
import qy.util
import misc

class gui(wx.Frame):
    ''' A simple GUI to talk to the SMC100 '''
    def __init__(self, pipe=None):
        ''' Constructor '''
        # Build the interface
        self.app = wx.App(False)
        self.build()

        # Periodically check for messages
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
        self.timer.Start(100)
        self.app.MainLoop()


    def ontimer(self, arg):
        ''' This function is called four times per second '''
        print 'awd'
        self.Update()


    def build(self):
        ''' Builds the various pieces of the GUI '''
        wx.Frame.__init__(self, None, title='SMC100 Motor Controller', size=(500,100))
        self.Bind(wx.EVT_CLOSE, self.quit)
        self.SetBackgroundColour((220,220,220))
        self.Show()


    def quit(self, *args):
        ''' Close down gracefully, and then destroy the window '''
        self.Destroy()



if __name__=='__main__':
    g=gui()
