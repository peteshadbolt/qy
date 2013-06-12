import numpy as np
from numpy.linalg import qr
from perm import perm
from python_perm import perm_ryser
import time
import sys

ntests=50
size=5

# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

# test c
t=time.clock()
for i in range(ntests):
    u=get_random_u(size)
    for j in range(ntests):
        p=perm(u)
t1=time.clock()-t

# test python
t=time.clock()
for i in range(ntests):
    u=get_random_u(size)
    for j in range(ntests):
        p=perm_ryser(u)
t2=time.clock()-t


print 'c time: %.6f' % t1
print 'python time: %.6f' % t2
