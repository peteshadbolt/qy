import qy
import qy.settings
import numpy
import os, json

# These functions do not really get used here, they are just for reference
def phasefunc(p, v): return p[1]+p[2]*(v**2)
def countfunc(p, phase): return p[0]*(1-p[5]*np.sin(phase)*np.sin(phase))
def fitfunc(p, voltage): return countfunc(p, phasefunc(p, voltage))
def errfunc(p, voltage, count): return np.sum(np.power(fitfunc(p, voltage)-count, 2))

class heater_calibration_table:
    def __init__(self, filename=None):
        ''' A heater calibration table, stored on disk, with lookup functions '''
        if filename==None: filename=os.path.join(qy.settings.get_config_path(), 'heater_calibration.json')
        self.filename=filename
        self.heater_count=0
        self.phase_voltage_curves=[]
        if os.path.exists(self.filename): self.load()

    def load(self, filename=None):
        ''' Load the table from a JSON file on disk '''
        f=open(self.filename, 'r')
        data=json.loads(f.read())
        f.close()
        self.phase_voltage_curves=data['phase_voltage_curves']
        self.heater_count=len(self.phase_voltage_curves)

    def save(self, filename=None):
        ''' Save to a JSON file on disk '''
        d={'heater_count':len(self.phase_voltage_curves), 'phase_voltage_curves':self.phase_voltage_curves}
        f=open(self.filename, 'w')
        f.write(json.dumps(d))
        f.close()

    def set_table(self, new_table):
        ''' Set the entire phase-voltage table '''
        self.phase_voltage_curves=new_table

    def get_voltage_from_phase(self, phase):
        ''' Get the appropriate voltage to set to the chip, given a phase '''

    def __str__(self):
        ''' Print the calibration table out as a string '''
        s='Heater calibration table [%s]\n' % self.filename
        for index, params in enumerate(self.phase_voltage_curves):
            s+='Heater %d: %s\n' % (index, str(params))
        return s


if __name__=='__main__':
    c=heater_calibration_table()
    c.phase_voltage_curves=[[0,1],[1,2]]
    c.save()
