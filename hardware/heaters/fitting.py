import numpy as np
from scipy.optimize import fmin


'''
First two parameters are for the phase-voltage relation.
Second two parameters are for the sinusoidal fit.
'''

def phase_voltage(p, v): return p[0]+p[1]*(v**2)
def counts_phase(p, phase): return p[2]*(1-p[3]*np.sin(phase/2)*np.sin(phase/2))
def counts_voltage(p, voltage): return counts_phase(p, phase_voltage(p, voltage))
def errfunc(p, voltage, count): return np.sum(np.power(counts_voltage(p, voltage)-count, 2))

def fit_fringe(voltages, counts, nfits=3, guess=None):
    ''' Fit a curve to some data '''

    # potentially choose a guess automatically
    if guess==None:
        p0 = np.array([0, .07, max(counts), (max(counts)-min(counts))/float(max(counts))])
    else:
        p0 = np.array(guess)

    # restart nelder-mead a few times
    for i in range(nfits):
        p0, best0, db, dc, warning = fmin(errfunc, p0, args=(voltages, counts), disp=0, full_output=1)
    return p0

