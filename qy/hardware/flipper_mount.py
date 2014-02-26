import serial

class flipper_mount:
	# Constructor
	def __init__(self, COM=4):
		self.serial=serial.Serial()
		self.serial.port=COM
		self.serial.timeout=10
		self.serial.baudrate=9600
		self.serial.bytesize=serial.EIGHTBITS
		self.serial.parity=serial.PARITY_NONE
		self.serial.stopbits=serial.STOPBITS_ONE
		self.initialize()
		
	def pulse(self):	
		''' send a pulse '''
		self.send('p')
						
	def initialize(self):	
		self.serial.open()
		self.serial.flush()
		print 'connected to mbed\n'
					
	def read(self):
		s=self.serial.readline(100)
		return s
		
	def send(self, s):
		self.serial.write(s)
		
	def kill(self):
		print 'closing mbed...'
		self.serial.close()