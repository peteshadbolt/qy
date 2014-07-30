'''
This file attempts to provide some guidance on style and coding based on your previous
heater class. In particular, look at how I am using timeouts to manage control flow.
'''

import serial
import time
import qy
import numpy
from pprint import pprint

class heaters:
    '''This class speaks to the heater driver through a serial port'''
    
    def __init__(self, port=None):
        '''Constructor for a heater object.'''
        print 'Connecting to heater driver...'
        self.serial=serial.Serial()
        self.serial.port=port
        self.serial.timeout=20
        self.baudrate=9600
        self.serial.bytesize=serial.EIGHTBITS
        self.serial.parity=serial.PARITY_NONE
        self.serial.stopbits=serial.STOPBITS_ONE
        self.heaters=8
		# Note vipall doesn't work for all heaters yet so leave self.heaters=8.  The heaters will still apply voltages
        try:
            self.serial.open()
            print 'Connected.'
        except serial.SerialException:
            print 'Failed!'
            
    def send_rcv(self, command):
        ''' Send a command, and return the response from the board '''
        self.serial.write(command + '\n')
        parrot=self.serial.readline() # The board "parrots" our command back to us
        response=self.serial.readline()
        return response.strip()

    def iterate(self, prefix, values):
        ''' Iterate over a list of values, sending one to each heater with a prefix'''
        responses=[]
        for heater_index, value in enumerate(values):
            command = '%s%d=%.9f' % (prefix, heater_index, value)
            response = self.send_rcv(command)
            responses.append(response)
        return responses

    def iterate_and_check(self, prefix, values):
        ''' Iterate over some values, and check that the board said 'OK' for each '''
        responses=self.iterate(prefix, values)
        assert(all([response=='OK' for response in responses]))
        return responses

    def send_voltages(self, voltages):
        '''Send multiple voltage commands and get a response'''
        self.iterate_and_check('v', voltages)
        return 'voltages are %s' % (str(voltages))
    
    def send_currents(self, currents):
        '''Send multiple currents commands and get a response'''
        self.iterate_and_check('i', currents)
        return 'currents are %s' % (str(currents))
            
    def send_powers(self, powers):
        '''Send multiple powers commands and get a response'''
        self.iterate_and_check('p', powers)
        return 'powers are %s' % (str(powers))
    
    def zero(self):
        '''zero all of the voltages'''
        response = self.send_rcv('vall=0')
        assert(response=='OK')
        return 'all zero'
    
    def query_all(self):
        '''Print out all V,I,P'''
        self.serial.write('vipall?\n')
        parrot = self.serial.readline() # The board "parrots" our command back to us
        responses = [self.serial.readline() for i in range(self.heaters)]
        return ''.join(responses)

    def dict(self):
		''' Dictionary for vip '''
		self.serial.write('vipall?\n')
		parrot = self.serial.readline() # The board "parrots" our command back to us
		output={}
		for i in range(self.heaters):
			s = self.serial.readline().replace(':',' ').split()
			voltage, current, power = float(s[1]), float(s[3]), float(s[5])
			this_heater={'voltage': voltage, 'current': current, 'power': power}
			output[i]=this_heater
		return output

    def help(self):
        ''' Help function '''
        # We don't actually know how long the help message will be. 
        # So we don't know when to stop waiting for new data.
        # So let's use a timeout to deal with this function (and only this one!)
        old_timeout=self.serial.timeout # Remember the previous timeout value
        self.serial.timeout=0.5 # Set it to a fast timeout
        self.serial.write('help\n')
        print ''.join(self.serial.readlines())
        self.serial.timeout=old_timeout # Restore the timeout
    
    def kill(self):
        '''Close the connection to the heater driver'''
        self.serial.close()
        print 'Disconnected from heater driver'


		# TODO -- a smart way to do VMAX on all
		
#TEST
if __name__=='__main__':

	# Create a heater called test
	#   test = heaters(port = '/dev/cu.usbserial')
	test = heaters(port = 'COM10')
	# Test it
	print test.send_rcv('v1=0')
	time.sleep(1)
	print test.send_voltages([0,0,0,0,0,0,0])
	time.sleep(1)
	print test.send_currents([0,0,0,0,0,0,0,0])
	time.sleep(1)
	print test.send_powers([0,0,0,0,0,0,0,0])
	time.sleep(1)
	print test.zero()
	time.sleep(1)
	print test.query_all()
	pprint(test.dict())

	test.kill()
	
	raw_input('Press Any Key To Exit')
	
	
