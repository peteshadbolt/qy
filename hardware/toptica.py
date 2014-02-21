import serial
import time

class toptica:
    def __init__(self, COM=3):
        print 'Connecting to laser on COM%d...' % (COM+1),
        self.serial=serial.Serial()
        self.serial.port=COM
        self.serial.timeout=10
        self.serial.baudrate=115200
        self.serial.bytesize=serial.EIGHTBITS
        self.serial.parity=serial.PARITY_NONE
        self.serial.stopbits=serial.STOPBITS_ONE
        self.serial.open()
        self.serial.flush()
        self.serial.write('en 2\r\n')
        s=self.serial.readline(100)
        print 'Done'
                
    def send(self, command):
        self.serial.write(command.strip()+'\r\n')
        return self.serial.readline(100)
                
    def la_on(self):
        self.serial.write('la on\r\n')
        self.serial.readline(100)
        print 'laser on'
        
    def la_off(self):
        self.serial.write('la off\r\n')
        self.serial.readline(100)
        print 'laser off'
        
    def set_pow(self, power):
        self.serial.write('set pow %d\r\n' % power)
        self.serial.readline(100)
        print 'laser power %d' % power
        
    def kill(self): 
        self.serial.write('la off\r\n')
        self.serial.readline(100)
        self.serial.close()
        print 'laser was shut down'
