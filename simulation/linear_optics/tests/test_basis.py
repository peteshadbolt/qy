from scipy.misc import comb
import numpy as np
from qy.simulation import linear_optics as lo

# testing combinatorial number systems
def convert(n,r,m):
    '''
    Encodes the input integer 'm' to a constant weight code of n-digits with r-ones
    Most significant digit at highest index.
    '''
    out=np.zeros(n*2)
    n=n-1
    while (n>=0):
        if (n>r & r>=0):
            y = comb(n-1,r, exact=True)
        else:
            y = 0;
     
        if (m>=y):
            m = m - y;
            out[n] = 1;
            r = r - 1;
        else:
            out[n] = 0;

        n += -1
    return out



nmodes=3
nphotons=2
d=comb(nphotons+nmodes-1, nphotons, exact=1)

for i in range(d):
    aa=convert(nmodes, nphotons, i)
    print i, aa, sum(aa)

