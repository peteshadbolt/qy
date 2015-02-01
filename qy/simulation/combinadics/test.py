import sys
import combi
from scipy.misc import comb, factorial
import time
from qy import util
import numpy as np


def choose(n, k):
    ''' n choose k '''
    out = 1
    if n < k:
        return 0
    for i in range(1, n - k + 1):
        out *= (i + k) / float(i)
    return int(out + .5)


def to_index(modes, p, m):
    out = 0
    mx = choose(m + p - 1, p)
    for i in range(1, p + 1):
        out += choose(m - modes[p - i] + i - 2, i)
    return mx - out - 1


def from_index(idx, p, m):
    mx = choose(m + p - 1, p)
    if idx >= mx:
        print 'Index out of range'
        return
    n = m + p - 1
    r = p
    i = 0
    y = 0
    modes = [0] * p
    idx = mx - idx - 1
    while n > 0:
        if n > r and r >= 0:
            y = choose(n - 1, r)
        else:
            y = 0
        if idx >= y:
            idx = idx - y
            modes[i] = m + p - 1 - n - i
            r += -1
            i += 1
        n += -1
    return modes


def get_normalization(modes):
    nonzeros = {}
    for mode in modes:
        if mode in nonzeros:
            nonzeros[mode] += 1
        else:
            nonzeros[mode] = 1
    total = 1
    for value in nonzeros.values():
        total *= factorial(value, exact=1)
    return total

#
# Check error reporting

print combi.to_index([1, 2, 3], 3, 1)
try:
    print combi.to_index([1, 2, 3], 4, 1)
except ValueError:
    print 'Got a value error'

#

# time factorial
t1 = time.clock()
for qq in range(1000):
    for q in range(10):
        combi.factorial(q)
t2 = time.clock()
print 'cython factorial', t2 - t1, ' seconds'

t1 = time.clock()
for qq in range(1000):
    for q in range(10):
        factorial(q)
t2 = time.clock()
print 'scipy factorial', t2 - t1, ' seconds'
print


#
# time normalization
t1 = time.clock()
for qq in range(1000):
    for size in [3, 4, 5, 6, 7]:
        q = np.random.randint(0, 6, size).tolist()
        combi.get_normalization(q)
t2 = time.clock()
print 'cython normalization', t2 - t1, ' seconds'

t1 = time.clock()
for qq in range(1000):
    for size in [3, 4, 5, 6, 7]:
        q = np.random.randint(0, 6, size).tolist()
        get_normalization(q)
t2 = time.clock()
print 'python normalization', t2 - t1, ' seconds'
print


#
# time basis mapping
t1 = time.clock()
for qq in range(10):
    for p in range(2, 5):
        # print p
        m = p ** 2
        N = combi.choose(m + p - 1, p)
        for index in xrange(combi.choose(m + p - 1, p)):
            combi.from_index(index, p, m)
            # util.progress_bar(index, N)
t2 = time.clock()
print 'cython basis mapping', t2 - t1, ' seconds'

t1 = time.clock()
for qq in range(10):
    for p in range(2, 5):
        # print p
        m = p ** 2
        N = combi.choose(m + p - 1, p)
        for index in xrange(combi.choose(m + p - 1, p)):
            from_index(index, p, m)
            # util.progress_bar(index, N)
t2 = time.clock()
print 'python basis mapping', t2 - t1, ' seconds'

print
