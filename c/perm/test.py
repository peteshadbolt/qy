import numpy as np
from numpy.linalg import qr
from perm import perm
from python_perm import perm_ryser
import time
import sys
from qy import util

# 5 photons in 21 modes
ntests=5313
size=4


# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

# check that we are actually calcualting the permanent!
for i in range(ntests):
    u=get_random_u(size)
    p1 = perm(u)
    p2 = perm_ryser(u)
    dist = np.abs(p1-p2)
    if dist>0.000000001:
        print 'DISCREPANCY!!!'
        print p1
        print p2

# test c
print 'C'
t=time.clock()
u=get_random_u(size)
for i in range(ntests):
    p=perm(u)
    #util.progress_bar(i/float(ntests))
t1=time.clock()-t

# test python
print '\nPython'
t=time.clock()
for i in range(ntests):
    p=perm_ryser(u)
    #util.progress_bar(i/float(ntests))
t2=time.clock()-t

print 'c time: %.6f' % t1
print 'python time: %.6f' % t2
