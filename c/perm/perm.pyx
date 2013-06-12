import numpy as np
cimport numpy as np
cimport cython

'''
Fast permanent in c. Under windows/mingw32 run with:
python setup.py build_ext --inplace -c m
'''


# typedefs
DTYPE = np.complex
ctypedef np.complex_t DTYPE_t

# safety off!
@cython.boundscheck(False)
def countbits(unsigned int n):
    ''' count the number of bits in a binary string ''' 
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
    return n

# safety off!
@cython.boundscheck(False)
def perm(np.ndarray[DTYPE_t, ndim=2] A not None):
    '''
    The permanent of a matrix
    m is a complex NxN numpy matrix
    '''

    cdef int n=A.shape[0]
    cdef int i=0
    cdef int z=0
    cdef int index=0
    cdef float y_real
    cdef float y_imag

    # iterate over exponentially many terms
    for i from 0 <= i < 2**n:
        count=countbits(i)
        for z from 0 <= z < n:
            index = i & 1<<z != 0
            y_real=y_real+y_real
            y_imag=y_imag+y_imag

    # get normalization constant
    cdef float norm=((-1)**n)

    return norm*y_real+1j*norm*y_imag


