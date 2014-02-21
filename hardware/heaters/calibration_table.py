import qy
import qy.settings
from qy.util import json_no_unicode
import numpy as np
import os, json

# These functions do not really get used here, they are just for reference
def phasefunc(p, v): return p[1]+p[2]*(v**2)
def countfunc(p, phase): return p[0]*(1-p[5]*np.sin(phase)*np.sin(phase))
def fitfunc(p, voltage): return countfunc(p, phasefunc(p, voltage))
def errfunc(p, voltage, count): return np.sum(np.power(fitfunc(p, voltage)-count, 2))

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
        print self.curve_parameters
        d={'heater_count':len(self.curve_parameters), 'curve_parameters':self.curve_parameters}
        f=open(self.filename, 'w')
        f.write(json.dumps(d), indent=4, sort_keys=True)
        f.close()
        print 'saved %s' % self.filename

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

    def get_voltage(self, heater_index, phase):
        ''' Get the appropriate voltage to set to the chip, given a phase '''
        p=self.get_parameters(heater_index)
        phase=phase % (2*np.pi)
        phase=phase-2*np.pi
        while p[0]>phase: phase=phase+2*np.pi
        v=np.sqrt((phase-float(p[0]))/float(p[1]))
        if v>7:
            phase=phase-2*np.pi
            v=self.get_voltage(heater_index,phase)
        return v if v>=0 else -v
        
    def get_voltages(self, phases):
        '''Turn a list of (8) phases in to a list of voltages'''
        if len(phases)!=8:
            print 'Please provide 8 phases'
            '''Is this the best way?'''
            exit()
        v=[self.get_voltage(heater_index,phase) for heater_index, phase in enumerate(phases)]
        return v
    
    def __str__(self):
        ''' Print the calibration table out as a string '''
        s='Heater calibration table [%s]\n%s heaters\n' % (self.filename,str(self.heater_count))
        for index, params in self.curve_parameters.iteritems():
            s+='Heater %s: %s\n' % (index, str(params))
        return s

if __name__=='__main__':
    c=calibration_table()
    print c.curve_parameters
    c.save()
    print c
