import serial
import time
import qy
from serial import SerialException

# constants pertaining to the SMC100
controller_state_map=\
	{'0A': 'NOT REFERENCED from reset',
	'0B': 'NOT REFERENCED from HOMING',
	'0C': 'NOT REFERENCED from CONFIGURATION',
	'0D': 'NOT REFERENCED from DISABLE',
	'0E': 'NOT REFERENCED from READY',
	'0F': 'NOT REFERENCED from MOVING',
	'10': 'NOT REFERENCED ESP stage error',
	'11': 'NOT REFERENCED from JOGGING',
	'14': 'CONFIGURATION',
	'1E': 'HOMING commanded from RS-232-C',
	'1F': 'HOMING commanded by SMC-RC',
	'28': 'MOVING',
	'32': 'READY from HOMING',
	'33': 'READY from MOVING',
	'34': 'READY from DISABLE',
	'35': 'READY from JOGGING',
	'3C': 'DISABLE from READY',
	'3D': 'DISABLE from MOVING',
	'3E': 'DISABLE from JOGGING',
	'46': 'JOGGING from READY',
	'47': 'JOGGING from DISABLE',
	'48': 'SIMULATION MODE'}
	
# more constants
error_names=\
	['Not used',
	'Not used',
	'Not used',
	'Not used',
	'Not used',
	'Not used',
	'80W output power exceeded',
	'DC voltage too low',
	'Wrong ESP stage',
	'Homing time out',
	'Following error',
	'Short circuit detection',
	'RMS current limit',
	'Peak current limit',
	'Positive end of run',
	'Negative end of run']
	
class mc_state:
	def __init__(self, mc_count):
		self.mc_count=mc_count
		self.positions=[None]*mc_count
		self.states=[None]*mc_count
		self.errors=[None]*mc_count
		
	def get_position(self, controller_index):
		return self.positions[controller_index-1]
		
	def format(self):
		s='motors: '
		for i in range(self.mc_count):
			s+='%d, %.9f, %s; ' % (i+1, self.positions[i], self.states[i])
		return s+'\n'
		
	def __str__(self):
		s=''
		for i in range(self.mc_count):
			s+='MC%d: ' % (i+1)
			s+='%.2fmm, ' % self.positions[i]
			s+='%s\n' % self.states[i]
		return s

class smc100:
	''' This class talks to an SMC100 motor controller through a serial port '''
	
	def __init__(self, COM=None, callback=None):	
		''' Constructor for an SMC100 object. Remember that python's COM port indexing starts at zero! '''
		self.callback=callback if callback!=None else lambda x: x
		self.serial=serial.Serial()
		if COM==None: COM=qy.settings.get('motors.com')
		print 'Connecting to SMC100 on COM%d...' % (COM+1),
		self.serial.port=COM
		self.serial.timeout=10
		self.serial.baudrate=57600
		self.serial.bytesize=serial.EIGHTBITS
		self.serial.parity=serial.PARITY_NONE
		self.serial.stopbits=serial.STOPBITS_ONE
		
		try:
			self.serial.open()
			print 'done.'
		except SerialException:
			self.serial=qy.hardware.dummy_motor()
			print 'failed!'
			print 'Using a dummy motor controller'
		
		self.motors_count=qy.settings.get('motors.count')
		self.state=mc_state(self.motors_count)
		for i in range(1, self.motors_count+1):
			self.get_info(i)
		self.callback(self.state)
		
	def get_info(self, mc):
		''' gets all of the info about some or all motor controllers '''
		self.get_position(mc)
		self.get_state(mc)
		self.get_errors(mc)
	
	def send(self, command):
		''' Send an arbitrary string to the device. Look in the SMC100 manual for more information '''
		self.serial.write(command+'\r\n')
		
	def send_rcv(self, command):
		''' Send a command and wait for a response. Used for instance when we ask the current position of the controller '''
		self.serial.write(command+'\r\n')
		return_value=self.serial.readline()
		return return_value[len(command):].strip()
		
	def home(self, controller):
		''' 'Home' a particular controller. Requires the index number of the target controller '''
		return self.send('%02dOR' % (controller))
				
	def move_absolute(self, controller, position):
		''' Move a particular controller to some absolute position '''
		return self.send('%02dPA%f' % (controller, position))
		
	def move(self, mc, position):
		''' move the motor controller in a high-level, robust way '''
		# if the controller is not in any of these states, then we are not happy
		allowed_states=['MOVING', 'HOMING', 'READY']
		self.move_absolute(mc, position)
		self.get_info(mc)
		while not self.state.states[mc-1].startswith('READY'):
			self.get_info(mc)
			if all([not self.state.states[mc-1]. startswith(x) for x in allowed_states]):
				print 'there was a problem with motor controller %d.' % mc
				print self.get_errors(mc)
				print 'attempting repair...'
				self.home(mc)
			self.callback(self.state)
			time.sleep(0.05)
		self.get_info(mc)
		self.callback(self.state)
		
	def stop_motion(self, controller):
		''' Stop motion of a given controller '''
		return self.send('%02dST' % (controller))
		
	def move_relative(self, controller, position):
		''' Move to a relative postion '''
		return self.send_rcv('%02dPR%f' % (controller, position))
		
	def get_position(self, controller):
		''' Get the current position of a given controller. Returns a floating point value in mm '''
		try:
			pos=float(self.send_rcv('%02dTP' % (controller)))
			self.state.positions[controller-1]=pos
		except ValueError:
			return 0
		
	def get_state(self, controller):
		''' Get the state of a controller e.g. "READY from MOVING" '''
		try:
			s=self.send_rcv('%02dTS' % (controller))
			controller_state=controller_state_map[s[-2:]]
			self.state.states[controller-1]=controller_state
			return controller_state
		except KeyError: 
			return 'Strange Error'
		
	def get_errors(self, controller):
		''' Returns a list of errors (as strings) for a given controller '''
		try:
			s = self.send_rcv('%02dTS' % (controller))
			errorstring = ''.join(['%04d' % int(bin(int(c,16))[2:]) for c in s[:-2]])
			errors=[error_names[i] for i in range(16) if errorstring[i]=='1']
			if len(errors)==0:
				errors=[None]
			self.state.errors[controller-1]=errors
			return errors
		except ValueError:
			return [None]
	
	def kill(self):
		''' Close the serial connection to the SMC100 '''
		self.serial.close()
		print 'Disconnected from SMC100'
