import serial
import time
import qy.settings


class powermeter:

    """ This class talks to the 6-channel power meter"""

    def __init__(self, COM=None):
        if COM == None:
            COM = qy.settings.get('powermeter.com')
        self.serial = serial.Serial()
        self.serial.port = COM
        self.serial.timeout = 10
        self.serial.baudrate = 9600
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE
        self.serial.open()

    def read(self):
        s = self.serial.readline(1000)
        try:
            return map(int, s.split(','))
        except ValueError:
            return [0] * 6

    def kill(self):
        """ Shut down the powermeter and close the serial port """
        self.serial.close()
        print 'Disconnected from powermeter'
