import numpy as np
cimport numpy as cnp
cnp.import_array()
cimport cython
from scipy.misc import comb

def binomial(int n, int k):
    ''' the binomial coefficient '''
    cdef long ntok = 1
    cdef long ktok = 1
    cdef long p = n-k
    if 0 <= k <= n:
        if k < p: p=k
        for t from 1 <= t < p+1:
            ntok *= n
            ktok *= t
            n -= 1 # useless?
        return ntok // ktok
    else:
        return 0

cdef int largestv(int a, int b, int x):
    ''' largest value v where v < a and (v choose b) <= x '''
    cdef int v = a - 1
    while binomial(v, b) > x:
        v+=-1
    return v

@cython.boundscheck(False)
@cython.wraparound(False)
def fock(int n, int k, int m):
    ''' return the mth lexicographic element of combination C(n,k) '''
    cdef cnp.ndarray[cnp.int_t, ndim=1] ans = np.zeros(k, dtype=int)
    cdef int a=n
    cdef int b=k
    
    # x is the dual of m
    cdef int x=(binomial(n, k)-1)-m

    for i from 0 <= i < k:
        ans[i]=largestv(a,b,x)
        x=x-binomial(ans[i],b)
        a=ans[i]
        b=b-1

    for i from 0 <= i < k:
        ans[i]= (n-1)-ans[i]

    return ans
