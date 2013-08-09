import numpy as np
cimport numpy as cnp
cnp.import_array()
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def choose(int n, int k):
    ''' n choose k '''
    cdef double out=1
    if n<k: return 0
    cdef int i
    for i from 1 <= i <= n-k:
        out *= (i+k)/<double>i
    return int(out+.5)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def toindex(modes, int p, int m):
    ''' 
    Maps a list of positions of p photons in m modes to an index.
    After Nick Russel.
    '''
    cdef int out=0
    cdef int mx = choose(m+p-1,p)
    cdef int i
    for i from 1 <= i <= p:
        out+=choose(m-modes[p-i]+i-2,i)
    return mx-out-1

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def fromindex(int idx, int p, int m):
    '''
    Maps an index to a list of positions of p photons in m modes.
    After Nick Russel.
    '''
    cdef int mx = choose(m+p-1,p)
    if idx>=mx: print 'Index out of range'; return
    cdef int n=m+p-1
    cdef int r=p
    cdef int i=0
    cdef int y=0
    modes = [0]*p
    idx = mx-idx-1
    while n>0:
        if n>r and r>=0:
            y = choose(n-1,r)
        else:
            y = 0
        if idx>=y:
            idx = idx-y
            modes[i] = m+p-1-n-i
            r+=-1
            i+=1
        n+=-1;
    return modes

