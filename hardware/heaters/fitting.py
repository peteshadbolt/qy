import numpy as np
from scipy.optimize import fmin

'''
Functions for fitting phase-voltage relations of resistive heaters
'''

def phase_voltage(p, v): 
    ''' Phase as a function of voltage '''
    return p[0]+p[1]*(v**2)

def counts_phase(p, phase): 
    ''' Counts (intensity) as a function of phase '''
    return p[2]*(1-p[3]*np.sin(phase/2)*np.sin(phase/2))

def counts_voltage(p, voltage): 
    ''' Counts as a function of voltage '''
    return counts_phase(p, phase_voltage(p, voltage))

def errfunc(p, voltage, count): 
    ''' Error function, used in fitting '''
    return np.sum(np.power(counts_voltage(p, voltage)-count, 2))

def fit_fringe(voltages, counts, nfits=3, guess=None):
    ''' Fit a phase-voltage curve to some fringelike data '''
    # potentially choose a guess automatically
    if guess==None:
        p0 = np.array([0, .07, max(counts), (max(counts)-min(counts))/float(max(counts))])
    else:
        p0 = np.array(guess)

    # restart nelder-mead a few times
    for i in range(nfits):
        p0, best0, db, dc, warning = fmin(errfunc, p0, args=(voltages, counts), disp=0, full_output=1)
    return p0

if __name__=='__main__':
    from matplotlib import pyplot as plt
    plt.plot(phase_voltage([0, .1], np.linspace(0, 7, 100)))
    plt.savefig('test_fitting.pdf')

