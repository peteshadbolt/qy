import numpy as np
from scipy.optimize import fmin

# Fitting stuff
#def phase(p, v): return p[1]+p[2]*(v**2)+p[3]*(v**3)+p[4]*(v**4)
def phasefunc(p, v): return p[1]+p[2]*(v**2)
def countfunc(p, phase): return p[0]*(1-p[5]*np.sin(phase)*np.sin(phase))
def fitfunc(p, voltage): return countfunc(p, phasefunc(p, voltage))
def errfunc(p, voltage, count): return np.sum(np.power(fitfunc(p, voltage)-count, 2))

def get_fit(voltages, counts, nfits=3):
    ''' Fit a curve to some data '''
    p0 = np.array([max(counts), np.pi/4, 0.09, 0.0045, -0.001, 1.0])
    for i in range(nfits):
        p0, best0, db, dc, warning = fmin(errfunc, p0, args=(voltages, counts), disp=0, full_output=1)

    p1 = np.array([max(counts), np.pi, 0.09, 0.0045, -0.001, 1.0])
    for i in range(nfits):
        p1, best1, db, dc, warning = fmin(errfunc, p1, args=(voltages, counts), disp=0, full_output=1)

    best_parameters=[p0, p1][best1<best0]

    fit_x=np.linspace(0, 7, 500)
    return {'parameters':best_parameters, 'voltages':fit_x, 'counts':fitfunc(best_parameters, fit_x)}

