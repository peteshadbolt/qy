import numpy as np
import qy
from nidaqmx import System
from nidaqmx import AnalogOutputTask

'''the card which we want to use'''
CARD_NAME='NI 9264'

class dac:
    def connect_nidaqmx(self):
        '''look at nidaqmx'''
        system=System()

        '''search for the card that we want to use'''
        card=None
        for dev in system.devices:
            if dev.get_product_type() == CARD_NAME: card=dev
        assert(card!=None)

        '''create the 8-channel task'''
        self.task = AnalogOutputTask()
        channels=card.get_analog_output_channels()[:8]
        for channel in channels:
            self.task.create_voltage_channel(channel, min_val=0, max_val=7)

        '''zero everything'''
        self.zero()
        
    def write_voltages(self, voltages):    
        av=np.array(voltages)
        if max(av)>7.0:
            print 'CANNOT WRITE VOLTAGES GREATER THAN 7.0V'
            voltages=[0,0,0,0,0,0,0,0]
            av=voltages
        self.task.write(voltages)
        print 'wrote', av.round(2)
    def zero(self):
        self.write_voltages([0,0,0,0,0,0,0,0])
        
    def __init__(self):
        print 'CNOT-MZ heater server\n'
        self.connect_nidaqmx()
    
