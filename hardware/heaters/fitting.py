import numpy as np
from scipy.optimize import fmin

# Fitting stuff
#def phase(p, v): return p[1]+p[2]*(v**2)+p[3]*(v**3)+p[4]*(v**4)

# first two parameters are for the phase-voltage relation.
# second two parameters are for the sinusoidal fit.

def phasefunc(p, v): return p[0]+p[1]*(v**2)
def countfunc(p, phase): return p[2]*(1-p[3]*np.sin(phase)*np.sin(phase))
def fitfunc(p, voltage): return countfunc(p, phasefunc(p, voltage))
def errfunc(p, voltage, count): return np.sum(np.power(fitfunc(p, voltage)-count, 2))

def fit_fringe(voltages, counts, nfits=3, phase_guess=-0.6):
    ''' Fit a curve to some data '''
    p0 = np.array([phase_guess, .07, max(counts), (max(counts)-min(counts))/float(max(counts))])
    #for i in range(nfits):
        #p0, best0, db, dc, warning = fmin(errfunc, p0, args=(voltages, counts), disp=0, full_output=1)

    params=p0

    return params

