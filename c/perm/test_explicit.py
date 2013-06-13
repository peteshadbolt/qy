import numpy as np
from numpy.linalg import qr
import python_perm 
import perm
import time
import sys
from qy import util

# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

def perm_4x4(a):
    ''' an explicit 4x4 permanent '''
    return a[0,0]*a[1,1]*a[2,2]*a[3,3] \
         + a[0,0]*a[1,1]*a[3,2]*a[2,3] \
         + a[0,0]*a[2,1]*a[1,2]*a[3,3] \
         + a[0,0]*a[2,1]*a[3,2]*a[1,3] \
         + a[0,0]*a[3,1]*a[1,2]*a[2,3] \
         + a[0,0]*a[3,1]*a[2,2]*a[1,3] \
         + a[1,0]*a[0,1]*a[2,2]*a[3,3] \
         + a[1,0]*a[0,1]*a[3,2]*a[2,3] \
         + a[1,0]*a[2,1]*a[0,2]*a[3,3] \
         + a[1,0]*a[2,1]*a[3,2]*a[0,3] \
         + a[1,0]*a[3,1]*a[0,2]*a[2,3] \
         + a[1,0]*a[3,1]*a[2,2]*a[0,3] \
         + a[2,0]*a[0,1]*a[1,2]*a[3,3] \
         + a[2,0]*a[0,1]*a[3,2]*a[1,3] \
         + a[2,0]*a[1,1]*a[0,2]*a[3,3] \
         + a[2,0]*a[1,1]*a[3,2]*a[0,3] \
         + a[2,0]*a[3,1]*a[0,2]*a[1,3] \
         + a[2,0]*a[3,1]*a[1,2]*a[0,3] \
         + a[3,0]*a[0,1]*a[1,2]*a[2,3] \
         + a[3,0]*a[0,1]*a[2,2]*a[1,3] \
         + a[3,0]*a[1,1]*a[0,2]*a[2,3] \
         + a[3,0]*a[1,1]*a[2,2]*a[0,3] \
         + a[3,0]*a[2,1]*a[0,2]*a[1,3] \
         + a[3,0]*a[2,1]*a[1,2]*a[0,3]

size=4
u=get_random_u(size)
print python_perm.perm_ryser(u)
print perm.perm_4x4(u)


# test speedup over different matrix sizes
size=4
ntests=10000 
print '\n\n-----\n%dx%d matrix (%d tests)' % (size, size, ntests)

# choose your weapons
perm_cython_ryser=perm.perm_ryser
perm_cython_explicit=perm.perm_4x4
perm_python=perm_4x4

print '\nTesting Cython...'
t=time.clock()
u=get_random_u(size)
for i in range(ntests):
    p=perm_cython_explicit(u)
    util.progress_bar(i/float(ntests))
t_cython_explicit=time.clock()-t

print '\nTesting Cython...'
t=time.clock()
u=get_random_u(size)
for i in range(ntests):
    p=perm_cython_ryser(u)
    util.progress_bar(i/float(ntests))
t_cython_ryser=time.clock()-t

print '\nTesting Python...'
t=time.clock()
for i in range(ntests):
    p=perm_python(u)
    util.progress_bar(i/float(ntests))
t_python=time.clock()-t

print '\nCython (explicit) time: %.6f' % t_cython_explicit
print '\nCython (Ryser) time: %.6f' % t_cython_ryser
print 'Python time: %.6f' % t_python

