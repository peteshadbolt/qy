import numpy as np
cimport numpy as cnp
cnp.import_array()
cimport cython

'''
Fast permanent in cython. Under windows/mingw32 compile with:
python setup.py build_ext --inplace -c mingw32
'''


# typedefs
DTYPE = np.complex
ctypedef cnp.complex_t DTYPE_t

def countbits(unsigned int n):
    ''' count the number of bits in a binary string ''' 
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
    return n

@cython.boundscheck(False)
@cython.wraparound(False)
def perm(cnp.ndarray[cnp.complex_t, ndim=2] A):
    cdef int n = A.shape[0]
    cdef float norm = (-1)**n
    cdef int i = 0
    cdef int z = 0
    cdef int y = 0
    cdef float y_real = 0
    cdef float y_imag = 0
    cdef float product_real = 0
    cdef float product_imag = 0
    cdef float prefactor = 0
    cdef cnp.complex_t aa

    #iterate over exponentially many terms
    for i from 0 <= i < 2**n:
        prefactor=(-1)**countbits(i)

        # for each term in the index string
        for z from 0 <= z < n:

            # if the column is marked
            if i & (1 << z) > 0:
                product_real = 1
                product_imag = 1

                # work over the row
                for y from 0 <= y < n:
                    aa = A[z,y]
                    #print aa
                    # complex multiplication
                    product_real = (product_real * aa.real) - (product_imag * aa.imag)
                    product_imag = (product_imag * aa.real) + (product_real * aa.imag)

                # add to the permanent
                y_real = y_real + prefactor*product_real
                y_imag = y_imag + prefactor*product_imag

    #get normalization constant
    return norm*y_real+1j*norm*y_imag
