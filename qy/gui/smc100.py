import wx
from multiprocessing import Process, Pipe
import qy.settings
import qy.util
import misc

class motor_block(wx.Panel):
    def __init__(self, parent, controller_address, state):
        ''' A chunk of motor controller stuff '''
        self.parent=parent
        self.controller_address=controller_address
        self.state=state
        wx.Panel.__init__(self, parent)
        self.SetDoubleBuffered(True)
        sizer=wx.BoxSizer(wx.VERTICAL)
            
        # The label
        top_sizer=wx.BoxSizer(wx.HORIZONTAL)
        bottom_sizer=wx.BoxSizer(wx.HORIZONTAL)
        label='MC%s (%s)'  % (controller_address, state['human_identifier'])
        self.label=wx.StaticText(self, label=label, size=(300,30))
        self.label.SetFont(wx.Font(10, wx.NORMAL, wx.NORMAL, wx.BOLD))
        top_sizer.Add(self.label, 1, wx.RIGHT|wx.EXPAND, border=5)

        # User input
        self.position_input=wx.TextCtrl(self, size=(100,20))
        self.position_input.SetValue(str(state['position']))
        top_sizer.Add(self.position_input, 0, wx.RIGHT, border=5)

        # Units
        self.unitlabel=wx.StaticText(self, label=state['unit'])
        top_sizer.Add(self.unitlabel, 0, wx.RIGHT, border=5)

        # Error label
        label='State: %s' % state['state']
        if len(state['errors'])>0: label+=' | Errors: %s'  % state['errors']
        self.errorlabel=wx.StaticText(self, label=label, size=(300,30))
        self.errorlabel.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL))
        bottom_sizer.Add(self.errorlabel, 0, wx.RIGHT, border=5)

        # The button saying "start moving"
        self.button=wx.Button(self, label='Go!', size=(30, 25))
        self.button.Bind(wx.EVT_BUTTON, self.request_position)


        # Nudge left/right
        self.nudge_left_button=wx.Button(self, label='<<', size=(30,25))
        self.nudge_right_button=wx.Button(self, label='>>', size=(30,25))
        self.nudge_left_button.Bind(wx.EVT_BUTTON, lambda x:self.nudge(sign=-1))
        self.nudge_right_button.Bind(wx.EVT_BUTTON, lambda x:self.nudge(sign=1))
        bottom_sizer.Add(self.nudge_left_button, 0, wx.RIGHT, border=3)
        bottom_sizer.Add(self.button, 0, wx.RIGHT, border=3)
        bottom_sizer.Add(self.nudge_right_button, 0)

        # Finish up
        sizer.Add(top_sizer, 1)
        sizer.Add(bottom_sizer, 1)
        self.SetSizerAndFit(sizer)


    def update(self, state):
        ''' Update the displayed state of the motor controller '''
        self.state=state
        self.position_input.SetValue(str(state['position']))
        label='State: %s' % state['state']
        if len(state['errors'])>0: label+=' | Errors: %s'  % state['errors']
        self.errorlabel.SetLabel(label)


    def nudge(self, sign):
        ''' The user pressed "nudge" '''
        new_position = self.state['position']+sign*self.parent.nudge_amount
        move_request={'controller_address': self.controller_address, 'position': new_position}
        self.parent.send(('move', move_request))

        
    def request_position(self, *args):
        ''' The user pressed "go", requesting a new MC position '''
        try:
            new_position = float(self.position_input.GetValue())
        except ValueError:
            print 'Invalid position!'
            return

        move_request={'controller_address': self.controller_address, \
                'position': new_position}
        self.parent.send(('move', move_request))


class gui_head(wx.Frame):
    ''' A simple GUI to talk to the SMC100 '''
    def __init__(self, pipe=None):
        ''' Constructor '''

        # Global settings
        self.nudge_amount = qy.settings.get('motors.nudge_amount')

        # Figure out where we should send/recieve data
        self.pipe=pipe
        self.poll = None if pipe==None else pipe.poll
        self.send = (lambda x: x) if pipe==None else pipe.send
        self.recv = (lambda x: x) if pipe==None else pipe.recv

        # Build the interface
        self.app = wx.App(False)
        self.build()
        #self.Bind(wx.EVT_SIZE, lambda x: x) 

        # Periodically check for messages
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.ontimer, self.timer)
        self.timer.Start(100)
        self.app.MainLoop()


    def handle_input(self, key, value):
        ''' Update the status box '''
        if key=='status':
            print value
        elif key=='populate':
            self.populate(value)
        elif key=='smc100_actuator_state':
            address=value['controller_address']
            self.blocks[address].update(value)
        elif key=='kill':
            self.quit()

    def populate(self, motor_model):
        ''' Populate the GUI according to the motor controller configuration'''
        self.blocks={}
        # Build a gui element for each motor
        for controller_address, actuator in motor_model.items():
            self.blocks[controller_address]=motor_block(self, controller_address, actuator)
            self.mainsizer.Add(self.blocks[controller_address], 0, wx.ALL, border=5)

        self.SetTitle('SMC100')
        self.Fit()

    def ontimer(self, arg):
        ''' This function is called four times per second '''
        # Look for messages coming down the pipe
        while self.pipe.poll():
            key, value=self.recv()
            self.handle_input(key, value)
        self.Update()


    def build(self):
        ''' Builds the various pieces of the GUI '''
        wx.Frame.__init__(self, None, title='Loading...', size=(500,100))
        self.Bind(wx.EVT_CLOSE, self.quit)
        self.SetBackgroundColour((212,208,200))
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizerAndFit(self.mainsizer)
        self.SetSize((200,100))
        self.Show()


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
