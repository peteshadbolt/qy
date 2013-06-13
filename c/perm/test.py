import numpy as np
from numpy.linalg import qr
import perm
import python_perm 
import time
import sys
from qy import util
from matplotlib import pyplot as plt

# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

# check consistency
ntests=100
size=6

# check that we are doing precise calculation (wrt numpy)
print 'checking consistency...'
for i in range(ntests):
    util.progress_bar(i/float(ntests))
    u=get_random_u(size)
    p1 = perm.perm_ryser(u)
    p2 = python_perm.perm_ryser(u)
    dist = np.abs(p1-p2)
    if dist>0.000000001:
        print 'FAILED!'
        print 'permanent from c:', p1
        print 'permanent from python', p2
        sys.exit()
print '\ndone.\n'

# test speedup over different matrix sizes
speedups=[]
maxsize=15
sizes = range(2,maxsize)
for size in sizes:
    ntests=1000 if size<10 else 10
    print '\n\n-----\n%dx%d matrix (%d tests)' % (size, size, ntests)

    # choose your weapons
    perm_cython=perm.perm_ryser
    perm_python=python_perm.perm_ryser

    print '\nTesting Cython...'
    t=time.clock()
    u=get_random_u(size)
    for i in range(ntests):
        p=perm_cython(u)
        util.progress_bar(i/float(ntests))
    t_cython=time.clock()-t

    print '\nTesting Python...'
    t=time.clock()
    for i in range(ntests):
        p=perm_python(u)
        util.progress_bar(i/float(ntests))
    t_python=time.clock()-t
    speedup=(t_python/t_cython)
    print '\nCython time: %.6f' % t_cython
    print 'Python time: %.6f' % t_python
    print 'Speedup: %.3f' % speedup
    speedups.append(speedup)

plt.clf()
plt.plot(sizes, speedups, 'k.-')
plt.xlabel('Matrix size nxn')
plt.ylabel('Estimated speedup')
plt.ylim(ymin=0)
plt.savefig('plot.pdf')
