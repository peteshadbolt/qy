import numpy as np
from numpy.linalg import qr
from perm import perm
from python_perm import perm_ryser
from python_perm import perm_ryser_explicit
import time
import sys
from qy import util

# 5 photons in 21 modes
ntests=5313
size=5


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
    p = perm(u)
    #print '({0.real:.7f} + {0.imag:.7f}j)'.format(p)
    #p = perm_ryser_explicit(u)
    print '({0.real:.7f} + {0.imag:.7f}j)'.format(p)
    p = perm_ryser(u)
    print '({0.real:.7f} + {0.imag:.7f}j)'.format(p)
    print
    raw_input()

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
