import qy
import qy.settings
from qy.util import json_no_unicode
import numpy as np
import os, json

class calibration_table:
    def __init__(self, filename=None):
        ''' A heater calibration table, stored on disk, with lookup functions '''
        if filename==None: filename=os.path.join(qy.settings.get_config_path(), 'heater_calibration.json')
        self.filename=filename
        self.heater_count=0
        self.curve_parameters={}
        if os.path.exists(self.filename): self.load()

    def load(self, filename=None):
        ''' Load the table from a JSON file on disk '''
        f=open(self.filename, 'r')
        data=json.loads(f.read(), object_hook=json_no_unicode)
        f.close()
        self.curve_parameters=data['curve_parameters']
        self.heater_count=len(self.curve_parameters)

    def save(self, filename=None):
        ''' Save to a JSON file on disk '''
        if filename!=None: self.filename=filename
        self.curve_parameters={key: tuple(value) for key, value in self.curve_parameters.items()}
        d={'heater_count':len(self.curve_parameters), 'curve_parameters':self.curve_parameters}
        f=open(self.filename, 'w')
        f.write(json.dumps(d, indent=4, sort_keys=True))
        f.close()
        #print 'saved %s' % self.filename

    def set_table(self, new_table):
        ''' Set the entire phase-voltage table '''
        self.curve_parameters=new_table

    def set_curve(self, heater_index, fit_parameters):
        ''' Set a single curve '''
        self.curve_parameters[heater_index]=fit_parameters

    def get_parameters(self, heater_index):
        ''' Get the full set of parameters for a particular heater '''
        try:
            p=self.curve_parameters[heater_index]
        except KeyError:
            p=self.curve_parameters[unicode(heater_index)]
        return p

    def get_voltage_from_phase(self, heater_index, phase):
        ''' Get the appropriate voltage to set to the chip, given a phase '''
        '''Assuming that phi=a+b*v^2'''
        p=self.get_parameters(heater_index)
        phase=phase%(2*np.pi)
        phase=phase-2*np.pi
        while p[0]>phase: phase=phase+2*np.pi
        v=np.sqrt((phase-float(p[0]))/float(p[1]))
        return v if v>=0 else -v
        
        
    def get_voltage_from_phase_2(self,heater_index,phase,initial=True):
        '''Assuming that phi= a+b*v^2+c*v'''
        p=self.get_parameters(heater_index)
        if initial:
            phase=phase%(2*np.pi)
        while p[2]**2<4*(p[0]-phase)*p[1] :
            phase=phase+2*np.pi
        alpha=np.sqrt(p[2]**2-4*(p[0]-phase)*p[1])
        if (alpha > p[2] and p[1]>0) or (alpha < p[2] and p[1]<0):
            return (-p[2]+alpha)/(2*p[1])
        else : 
            phase+=2*np.pi
            return self.get_voltage_from_phase_2(heater_index,phase,initial=False)
         
        
    def get_voltages(self, phases):
        '''Turn a list of (8) phases in to a list of voltages'''
        v=[self.get_voltage_from_phase(heater_index,phase) for heater_index, phase in enumerate(phases)]
        return v
    
    def __str__(self):
        ''' Print the calibration table out as a string '''
        s='Heater calibration table [%s]\n%s heaters\n' % (self.filename,str(self.heater_count))
        for index, params in self.curve_parameters.iteritems():
            s+='Heater %s: %s\n' % (index, str(params))
        return s

if __name__=='__main__':
    c=calibration_table()

    for i in range(100):
        for heater_index in range(7):
            v=c.get_voltage_from_phase_2(heater_index, np.random.uniform(-np.pi*4, np.pi*4))
            #print v
            if not 0<=v<=7:
                print 'fail'
                print v

    c.save()
