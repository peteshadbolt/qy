import time
import serial
import time
import qy
from serial import SerialException


# Constants pertaining to the SMC100
controller_state_map =\
    {'0A': 'NOT REFERENCED from reset', '0B': 'NOT REFERENCED from HOMING', '0C': 'NOT REFERENCED from CONFIGURATION',
     '0D': 'NOT REFERENCED from DISABLE', '0E': 'NOT REFERENCED from READY', '0F': 'NOT REFERENCED from MOVING',
     '10': 'NOT REFERENCED ESP stage error', '11': 'NOT REFERENCED from JOGGING', '14': 'CONFIGURATION',
     '1E': 'HOMING commanded from RS-232-C', '1F': 'HOMING commanded by SMC-RC', '28': 'MOVING', '32': 'READY from HOMING', '33': 'READY from MOVING', '34': 'READY from DISABLE', '35': 'READY from JOGGING', '3C': 'DISABLE from READY', '3D': 'DISABLE from MOVING',
     '3E': 'DISABLE from JOGGING', '46': 'JOGGING from READY', '47': 'JOGGING from DISABLE', '48': 'SIMULATION MODE'}

error_names =\
    ['Not used', 'Not used', 'Not used', 'Not used',
     'Not used', 'Not used', '80W output power exceeded', 'DC voltage too low',
     'Wrong ESP stage', 'Homing time out', 'Following error', 'Short circuit detection',
     'RMS current limit', 'Peak current limit', 'Positive end of run', 'Negative end of run']

human_actuator_names = {'LTA-HL': 'High load linear actuator',
                        'LTA-HS': 'High speed linear actuator',  'PR50CC': 'Rotation stage'}
unit_table = {'LTA-HL': 'mm', 'LTA-HS': 'mm', 'PR50CC': 'deg'}
tag_table = {'LTA-HL': 'LIN', 'LTA-HS': 'LIN', 'PR50CC': 'ROT'}
MAX_CONTROLLERS = 6


class smc100_actuator:

    ''' A single actuator '''

    def __init__(self, controller_address, serial, callback=None):
        self.callback = callback if callback != None else lambda x: x
        self.controller_address = controller_address
        self.serial = serial
        self.characterize()

    def characterize(self):
        ''' The actuator characterizes itself '''
        self.identify_stage()
        self.update()

    def identify_stage(self):
        ''' Read the stage identifier of this actuator from the SMC100 '''
        self.send('ID?')
        self.stage_identifier = self.serial.readline()[
            4:].strip().split('_')[0]
        self.human_identifier = human_actuator_names[self.stage_identifier]
        self.tag = '%s%s' % (
            self.controller_address, tag_table[self.stage_identifier])
        self.unit = unit_table[self.stage_identifier]

    def update(self):
        ''' Update position, state and errors '''
        self.get_position()
        self.get_state_and_errors()
        # self.callback(self.dict())

    def get_position(self):
        ''' Read the position of this actuator '''
        self.position = float(self.send_rcv('TP'))

    def get_state_and_errors(self):
        ''' Read the position of this actuator '''
        s = self.send_rcv('TS')
        t = s[-2:]
        self.state = controller_state_map[
            t] if t in controller_state_map else 'Unknown state'
        errorstring = ''.join(
            ['%04d' % int(bin(int(c, 16))[2:]) for c in s[:-2]])
        self.errors = [error_names[i]
                       for i in range(16) if errorstring[i] == '1']

    def home(self):
        ''' 'Home' this controller '''
        self.send('OR')

    def repair(self):
        ''' Repair this controller '''
        if self.state.startswith('DISABLE'):
            self.send('MM1')
            self.update()
        self.home()

    def move(self, position):
        ''' move the motor controller in a high-level, robust way '''
        allowed_states = ['MOVING', 'HOMING', 'READY']
        self.send('PA%f' % position)
        self.update()
        while not self.state.startswith('READY'):
            self.callback(('smc100_actuator_state', self.dict()))
            time.sleep(0.05)
            self.update()
            if all([not self.state.startswith(x) for x in allowed_states]):
                print 'There was a problem with motor controller %s.' % self.tag
                print 'Attempting repair...'
                self.repair()
        self.update()
        self.callback(('smc100_actuator_state', self.dict()))

    def send(self, command):
        ''' Send an arbitrary string to the device. Look in the SMC100 manual for more information '''
        command = '%02d%s' % (self.controller_address, command)
        self.serial.write(command + '\r\n')

    def send_rcv(self, command):
        ''' Send a command and wait for a response. Used for instance when we ask the current position of the controller '''
        command = '%02d%s' % (self.controller_address, command)
        self.serial.write(command + '\r\n')
        return_value = self.serial.readline()
        return return_value[len(command):].strip()

    def __str__(self):
        ''' Return a description of this actuator including the realtime state '''
        s = '%s: %s\n%s\n' % (
            self.tag, self.human_identifier, self.stage_identifier)
        s += 'Position: %.5f %s\n' % (self.position, self.unit)
        s += 'State: %s\n' % (self.state)
        s += 'Errors: %s\n' % (self.errors)
        s += '\n'
        return s

    def dict(self):
        ''' Return a dictionary containing the state, etc. Useful for sending down pipes'''
        return {'controller_address': self.controller_address,
                'tag': self.tag,
                'human_identifier': self.human_identifier,
                'stage_identifier': self.stage_identifier,
                'position': self.position,
                'unit': self.unit,
                'state': self.state,
                'errors': self.errors}


class smc100:

    ''' This class talks to an SMC100 motor controller through a serial port '''

    def __init__(self, serial_port=None, callback=None):
        ''' Constructor for an SMC100 object. Remember that python's COM port indexing starts at zero! '''
        # set up callbacks
        self.callback = callback if callback != None else lambda x: x

        # try to open the serial port
        self.open_serial_port(serial_port)
        self.validate_serial_port()

        # characterise the motor controllers
        self.build_model()

    def move(self, controller_address, position):
        ''' Move a particular motor controller '''
        self.actuators[controller_address].move(position)

    def update(self):
        ''' Update all controllers '''
        output = {}
        for controller_address, actuator in self.actuators.items():
            actuator.update()
            output[controller_address] = a.dict()
        return output

    def open_serial_port(self, serial_port=None):
        ''' Tries to connect to the serial port '''
        self.serial = serial.Serial()
        self.serial.port = int(
            qy.settings.get('motors.com')) if serial_port == None else serial_port
        self.serial_port = self.serial.port
        self.serial.timeout = .5
        self.serial.baudrate = 57600
        self.serial.bytesize = serial.EIGHTBITS
        self.serial.parity = serial.PARITY_NONE
        self.serial.stopbits = serial.STOPBITS_ONE

        self.callback(
            ('status', 'Connecting to SMC100 on COM%d...' % (self.serial_port + 1)))
        self.serial_open = False
        self.serial.open()
        self.serial_open = True
        self.callback(
            ('status', 'Connected to COM%d.' % (self.serial_port + 1)))

    def validate_serial_port(self):
        ''' Validates the connection to the serial port '''
        self.validated = False
        if not self.serial_open:
            return
        self.callback(('status', 'Validating serial port...'))
        s = self.send_rcv('TS', 1)[-2:]

        try:
            x = controller_state_map[s]
            self.validated = True
            self.callback(('status', 'Validated serial port ok'))
        except KeyError:
            self.close_serial_port()
            self.serial_open = False
            self.validated = False
            self.callback(('status', 'SMC100 serial port did not validate'))

    def build_model(self):
        ''' Builds an object model of all the connected motor controllers '''
        self.callback(('status', 'Characterising motors...'))
        self.actuators = {}
        for controller_address in range(MAX_CONTROLLERS):
            state = self.send_rcv('TS', controller_address)
            if len(state) > 0:
                actuator = smc100_actuator(
                    controller_address, self.serial, self.callback)
                self.callback(
                    ('status', 'Found an actuator (%s)' % actuator.human_identifier))
                self.actuators[controller_address] = actuator

        self.motors_count = len(self.actuators)
        self.callback(('status', 'Finished characterising motors'))

    def close_serial_port(self):
        ''' Close the serial port '''
        if not self.serial_open:
            return
        self.serial.close()
        self.serial_open = False
        self.validated = False
        print 'Closed SMC100 serial port'

    def kill(self):
        ''' Close the serial connection to the SMC100 '''
        self.close_serial_port()
        print 'Disconnected from SMC100'

    def send_rcv(self, command, controller_address):
        ''' Send a command and wait for a response. Used for instance when we ask the current position of the controller '''
        command = '%02d%s' % (controller_address, command)
        self.serial.write(command + '\r\n')
        return_value = self.serial.readline()
        return return_value[len(command):].strip()

    def dict(self):
        ''' Get a dictionary representing the full hardware model '''
        return {key: value.dict() for key, value in self.actuators.items()}

    def __str__(self):
        ''' Summarise the motor controller model '''
        s = '\nSMC100 motor controller on COM%d (python %d)\n' % (
            self.serial_port + 1, self.serial_port)
        for controller_address, actuator in self.actuators.items():
            s += 'Controller %s:' % controller_address
            s += str(actuator) + '\n'
        return s
