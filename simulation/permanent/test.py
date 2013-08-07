import numpy as np
from numpy.linalg import qr
from qy.simulation import permanent
from matplotlib import pyplot as plt
import time

def get_perm(accelerate, hard, size):
    ''' get the permanent function '''
    if accelerate:
        if not hard: return permanent.perm_ryser
        if size == 2: return permanent.perm_2x2
        if size == 3: return permanent.perm_3x3
        if size == 4: return permanent.perm_4x4
        return permanent.perm_ryser
    else:
        if not hard: return permanent.perm_ryser_p
        if size == 2: perm=permanent.perm_2x2_p
        if size == 3: return permanent.perm_3x3_p
        if size == 4: return permanent.perm_4x4_p
        return permanent.perm_ryser_p

# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

def plot_times(accelerate, hard, max_size=13, ntests=100, nloops=10, color='black', label='awd'):
    x=[]
    y=[]
    err=[]
    for size in range(2, max_size):
        print size
        perm=get_perm(accelerate, hard, size)
        test_data=[get_random_u(size) for i in range(ntests)]
        data=[]
        for loop in range(nloops):
            t1=time.clock()
            q=map(perm, test_data)
            t2=time.clock()
            data.append((t2-t1)/(ntests*nloops))
        x.append(size)
        y.append(np.average(data))
        err.append(np.std(data))

    plt.errorbar(x, y, yerr=err, fmt='.-', ms=7, color=color, mec=color, label=label)


plt.clf()
plot_times(0, 0, color='red', max_size=7, label='Ryser Python')
plot_times(1, 0, color='blue', label='Ryser Cython')
plot_times(0, 1, color='green', max_size=5, label='Hard Python')
plot_times(1, 1, color='black', max_size=5, label='Hard Cython')
plt.legend(loc=2, prop={'size':9})
plt.yscale('log')
plt.xlabel('$N$')
plt.ylabel('$t$, seconds')
plt.grid(color='gray')
plt.savefig('benchmark.pdf')
