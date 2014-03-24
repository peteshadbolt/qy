import numpy as np
import os, json, sys
from calibration_table import calibration_table
from dac import dac
from qy.hardware import fpga

###TODO:
###-return counts before cooling?
###-remove dependency on nidaqmx?
###-make wrapper for heaters for TCP/IP

def test_callback(s):
    print 'got this information: %s' % s
    
def callback_print_string(s):
    print s
    
'''Everything needed to run an experiment is in heaters. dac and table just do background stuff'''
class heaters:
    def __init__(self):
        self.dac=dac()
        self.calibration_table=calibration_table()
        self.dac.zero()
        self.ontime=2
        self.offtime=15
        self.integration_time=1

    def cool(self, callback=None):
        self.dac.zero()
        time.sleep(self.offtime)
    
    def pulse(self,phases,callback=callback_print_string):
        voltages=self.calibration_table.get_voltages(phases)
        self.dac.write_voltages(voltages)
        for i in range(self.integration_time):
            if callback!=None: callback('Integrating [%.3f %% done]...' % (100*(i)/float(self.integration_time)))
            for j in range(self.ontime): self.fpga.read()
            counts+=c
            self.cool(callback)
            if i == (self.integration_time-1) and callback!=None: callback('Integrating [100 % done]')
        return counts
        
    def set_ontime(self, ontime=2):
        self.ontime=ontime
        
    def set_offtime(self, offtime=15):
        self.offtime=offtime
        
    def set_integration_time(self, integration_time=1):
        self.integration_time=integration_time

    def kill(self):
        self.dac.zero()
        self.fpga.kill()
    
    def zero(self):
        self.dac.zero()
        
    def __str__(self):
        '''print out some information about the instance of heaters'''
        s='Heater settings:\nIntegration time = %i\nHeater on-time = %i\nHeater off-time = %i\n' % (self.integration_time, self.ontime, self.offtime)
        s+=str(self.calibration_table)
        return s
    
if __name__=='__main__':
    h=heaters()
    print h
    phases=[np.pi for i in range(8)]
    counts=h.pulse(phases, callback=callback_print_string)
    print counts
    
