import serial
import time
import qy


class chameleon:

    ''' This class talks to a Coherent Chameleon through a serial port '''

    def __init__(self, COM=None):
        ''' Constructor for a chameleon object. Remember that python's COM port indexing starts at zero! '''
        self.serial = serial.Serial()
        if COM == None:
            COM = qy.settings.lookup('chameleon.com')
        print 'Connecting to Chameleom on COM%d...' % (COM + 1),
        self.serial.port = COM
        self.serial.timeout = 10
        self.serial.baudrate = 19200
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        try:
            self.serial.open()
            print 'done.'
        except serial.SerialException:
            self.serial = qy.hardware.dummy_laser()
            print 'failed!'
            print 'Using a dummy laser'

        self.send_rcv('PROMPT=0')

    def send_rcv(self, command):
        ''' Send a command and wait for a response. '''
        self.serial.write(command + '\r\n')
        return_value = self.serial.readline()
        return return_value[len(command) + 1:]

    def get_shutter_state(self):
        ''' Figure out if the shutter is open or closed '''
        return int(self.send_rcv('?S'))

    def close_shutter(self):
        ''' Close the shutter '''
        return self.send_rcv('S=0')

    def kill(self):
        ''' Close the serial connection to the SMC100 '''
        self.serial.close()
        print 'Disconnected from Chameleon'
