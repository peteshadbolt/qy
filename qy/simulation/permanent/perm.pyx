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

'''
Helper functions start here
'''

def countbits(unsigned int n):
    ''' count the number of bits in a binary string ''' 
    n = (n & 0x5555555555555555) + ((n & 0xAAAAAAAAAAAAAAAA) >> 1)
    n = (n & 0x3333333333333333) + ((n & 0xCCCCCCCCCCCCCCCC) >> 2)
    n = (n & 0x0F0F0F0F0F0F0F0F) + ((n & 0xF0F0F0F0F0F0F0F0) >> 4)
    n = (n & 0x00FF00FF00FF00FF) + ((n & 0xFF00FF00FF00FF00) >> 8)
    n = (n & 0x0000FFFF0000FFFF) + ((n & 0xFFFF0000FFFF0000) >> 16)
    n = (n & 0x00000000FFFFFFFF) + ((n & 0xFFFFFFFF00000000) >> 32) # This last & isn't strictly necessary.
    return n

def parity(unsigned int n):
    ''' get the parity as -1 or +1 ''' 
    return -1 if (countbits(n) & 1) else 1

'''
Main permanent functions begin here.
Available:
    perm_ryser
    perm_2x2
    perm_3x3
    perm_4x4
    perm_5x5
''' 
@cython.boundscheck(False)
@cython.wraparound(False)
def perm_ryser(cnp.ndarray[cnp.complex_t, ndim=2] A):
    ''' Permanent using Ryser's algorithm '''
    cdef int n = A.shape[0]
    cdef int i = 0
    cdef int z = 0
    cdef int y = 0
    cdef double perm_real = 0
    cdef double perm_imag = 0
    cdef double product_real = 0
    cdef double product_real_old = 0
    cdef double product_imag = 0
    cdef double sum_real = 0
    cdef double sum_imag = 0
    cdef int sign = 0
    cdef cnp.complex_t aa

    #iterate over exponentially many index strings
    for i from 0 <= i < 2**n:
        product_real = 1
        product_imag = 0

        # iterate over rows
        for y from 0 <= y < n:

            # zero the sum
            sum_real = 0; sum_imag = 0;

            # for each column
            for z from 0 <= z < n:
                # if the column is marked, add it to the sum
                if i & (1 << z) > 0:
                    aa = A[z,y]
                    sum_real = sum_real + aa.real
                    sum_imag = sum_imag + aa.imag

            # multiply the sum into the product (complex multiplication)
            product_real_old = product_real * 1
            product_real = (product_real * sum_real) - (product_imag * sum_imag)
            product_imag = (product_imag * sum_real) + (product_real_old * sum_imag)

        # add to the permanent
        #sign=(-1)**countbits(i)
        sign=parity(i)
        perm_real = perm_real + sign*product_real
        perm_imag = perm_imag + sign*product_imag

    cdef int sign2 = (-1)**n
    return sign2*perm_real+1j*sign2*perm_imag

@cython.boundscheck(False)
@cython.wraparound(False)
def perm_ryser_real(cnp.ndarray[cnp.float_t, ndim=2] A):
    ''' Permanent according to Ryser's algorithm, real part only. This can be done in polynomial time! '''
    cdef int n = A.shape[0]
    cdef int i = 0
    cdef int z = 0
    cdef int y = 0
    cdef double perm = 0
    cdef double product = 0
    cdef double summed = 0
    cdef int sign = 0

    #iterate over exponentially many index strings
    for i from 0 <= i < 2**n:
        product= 1
        # iterate over rows
        for y from 0 <= y < n:
            summed = 0

            # for each column
            # if the column is marked, add it to the sum
            for z from 0 <= z < n:
                if i & (1 << z) > 0: summed = summed + A[z,y]
            product = product * summed

        # add to the permanent
        perm = perm + parity(i) * product
    return (-1)**n*perm

'''
Below are explicit permanents. these are NOT exploiting cython very well:
this is due to silly problems with complex numbers. The 3x3 is pretty fast though.
'''

def perm_2x2(cnp.ndarray a):
    ''' an explicit 2x2 permanent '''
    return a[0,0]*a[1,1] \
         + a[1,0]*a[0,1]

def perm_3x3(cnp.ndarray a):
    ''' an explicit 3x3 permanent '''
    return a[0,0]*a[1,1]*a[2,2] \
         + a[0,0]*a[2,1]*a[1,2] \
         + a[1,0]*a[0,1]*a[2,2] \
         + a[1,0]*a[2,1]*a[0,2] \
         + a[2,0]*a[0,1]*a[1,2] \
         + a[2,0]*a[1,1]*a[0,2]

def perm_4x4(cnp.ndarray a):
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

def perm_5x5(cnp.ndarray a):
    ''' an explicit 5x5 permanent '''
    return a[0,0]*a[1,1]*a[2,2]*a[3,3]*a[4,4] \
         + a[0,0]*a[1,1]*a[2,2]*a[4,3]*a[3,4] \
         + a[0,0]*a[1,1]*a[3,2]*a[2,3]*a[4,4] \
         + a[0,0]*a[1,1]*a[3,2]*a[4,3]*a[2,4] \
         + a[0,0]*a[1,1]*a[4,2]*a[2,3]*a[3,4] \
         + a[0,0]*a[1,1]*a[4,2]*a[3,3]*a[2,4] \
         + a[0,0]*a[2,1]*a[1,2]*a[3,3]*a[4,4] \
         + a[0,0]*a[2,1]*a[1,2]*a[4,3]*a[3,4] \
         + a[0,0]*a[2,1]*a[3,2]*a[1,3]*a[4,4] \
         + a[0,0]*a[2,1]*a[3,2]*a[4,3]*a[1,4] \
         + a[0,0]*a[2,1]*a[4,2]*a[1,3]*a[3,4] \
         + a[0,0]*a[2,1]*a[4,2]*a[3,3]*a[1,4] \
         + a[0,0]*a[3,1]*a[1,2]*a[2,3]*a[4,4] \
         + a[0,0]*a[3,1]*a[1,2]*a[4,3]*a[2,4] \
         + a[0,0]*a[3,1]*a[2,2]*a[1,3]*a[4,4] \
         + a[0,0]*a[3,1]*a[2,2]*a[4,3]*a[1,4] \
         + a[0,0]*a[3,1]*a[4,2]*a[1,3]*a[2,4] \
         + a[0,0]*a[3,1]*a[4,2]*a[2,3]*a[1,4] \
         + a[0,0]*a[4,1]*a[1,2]*a[2,3]*a[3,4] \
         + a[0,0]*a[4,1]*a[1,2]*a[3,3]*a[2,4] \
         + a[0,0]*a[4,1]*a[2,2]*a[1,3]*a[3,4] \
         + a[0,0]*a[4,1]*a[2,2]*a[3,3]*a[1,4] \
         + a[0,0]*a[4,1]*a[3,2]*a[1,3]*a[2,4] \
         + a[0,0]*a[4,1]*a[3,2]*a[2,3]*a[1,4] \
         + a[1,0]*a[0,1]*a[2,2]*a[3,3]*a[4,4] \
         + a[1,0]*a[0,1]*a[2,2]*a[4,3]*a[3,4] \
         + a[1,0]*a[0,1]*a[3,2]*a[2,3]*a[4,4] \
         + a[1,0]*a[0,1]*a[3,2]*a[4,3]*a[2,4] \
         + a[1,0]*a[0,1]*a[4,2]*a[2,3]*a[3,4] \
         + a[1,0]*a[0,1]*a[4,2]*a[3,3]*a[2,4] \
         + a[1,0]*a[2,1]*a[0,2]*a[3,3]*a[4,4] \
         + a[1,0]*a[2,1]*a[0,2]*a[4,3]*a[3,4] \
         + a[1,0]*a[2,1]*a[3,2]*a[0,3]*a[4,4] \
         + a[1,0]*a[2,1]*a[3,2]*a[4,3]*a[0,4] \
         + a[1,0]*a[2,1]*a[4,2]*a[0,3]*a[3,4] \
         + a[1,0]*a[2,1]*a[4,2]*a[3,3]*a[0,4] \
         + a[1,0]*a[3,1]*a[0,2]*a[2,3]*a[4,4] \
         + a[1,0]*a[3,1]*a[0,2]*a[4,3]*a[2,4] \
         + a[1,0]*a[3,1]*a[2,2]*a[0,3]*a[4,4] \
         + a[1,0]*a[3,1]*a[2,2]*a[4,3]*a[0,4] \
         + a[1,0]*a[3,1]*a[4,2]*a[0,3]*a[2,4] \
         + a[1,0]*a[3,1]*a[4,2]*a[2,3]*a[0,4] \
         + a[1,0]*a[4,1]*a[0,2]*a[2,3]*a[3,4] \
         + a[1,0]*a[4,1]*a[0,2]*a[3,3]*a[2,4] \
         + a[1,0]*a[4,1]*a[2,2]*a[0,3]*a[3,4] \
         + a[1,0]*a[4,1]*a[2,2]*a[3,3]*a[0,4] \
         + a[1,0]*a[4,1]*a[3,2]*a[0,3]*a[2,4] \
         + a[1,0]*a[4,1]*a[3,2]*a[2,3]*a[0,4] \
         + a[2,0]*a[0,1]*a[1,2]*a[3,3]*a[4,4] \
         + a[2,0]*a[0,1]*a[1,2]*a[4,3]*a[3,4] \
         + a[2,0]*a[0,1]*a[3,2]*a[1,3]*a[4,4] \
         + a[2,0]*a[0,1]*a[3,2]*a[4,3]*a[1,4] \
         + a[2,0]*a[0,1]*a[4,2]*a[1,3]*a[3,4] \
         + a[2,0]*a[0,1]*a[4,2]*a[3,3]*a[1,4] \
         + a[2,0]*a[1,1]*a[0,2]*a[3,3]*a[4,4] \
         + a[2,0]*a[1,1]*a[0,2]*a[4,3]*a[3,4] \
         + a[2,0]*a[1,1]*a[3,2]*a[0,3]*a[4,4] \
         + a[2,0]*a[1,1]*a[3,2]*a[4,3]*a[0,4] \
         + a[2,0]*a[1,1]*a[4,2]*a[0,3]*a[3,4] \
         + a[2,0]*a[1,1]*a[4,2]*a[3,3]*a[0,4] \
         + a[2,0]*a[3,1]*a[0,2]*a[1,3]*a[4,4] \
         + a[2,0]*a[3,1]*a[0,2]*a[4,3]*a[1,4] \
         + a[2,0]*a[3,1]*a[1,2]*a[0,3]*a[4,4] \
         + a[2,0]*a[3,1]*a[1,2]*a[4,3]*a[0,4] \
         + a[2,0]*a[3,1]*a[4,2]*a[0,3]*a[1,4] \
         + a[2,0]*a[3,1]*a[4,2]*a[1,3]*a[0,4] \
         + a[2,0]*a[4,1]*a[0,2]*a[1,3]*a[3,4] \
         + a[2,0]*a[4,1]*a[0,2]*a[3,3]*a[1,4] \
         + a[2,0]*a[4,1]*a[1,2]*a[0,3]*a[3,4] \
         + a[2,0]*a[4,1]*a[1,2]*a[3,3]*a[0,4] \
         + a[2,0]*a[4,1]*a[3,2]*a[0,3]*a[1,4] \
         + a[2,0]*a[4,1]*a[3,2]*a[1,3]*a[0,4] \
         + a[3,0]*a[0,1]*a[1,2]*a[2,3]*a[4,4] \
         + a[3,0]*a[0,1]*a[1,2]*a[4,3]*a[2,4] \
         + a[3,0]*a[0,1]*a[2,2]*a[1,3]*a[4,4] \
         + a[3,0]*a[0,1]*a[2,2]*a[4,3]*a[1,4] \
         + a[3,0]*a[0,1]*a[4,2]*a[1,3]*a[2,4] \
         + a[3,0]*a[0,1]*a[4,2]*a[2,3]*a[1,4] \
         + a[3,0]*a[1,1]*a[0,2]*a[2,3]*a[4,4] \
         + a[3,0]*a[1,1]*a[0,2]*a[4,3]*a[2,4] \
         + a[3,0]*a[1,1]*a[2,2]*a[0,3]*a[4,4] \
         + a[3,0]*a[1,1]*a[2,2]*a[4,3]*a[0,4] \
         + a[3,0]*a[1,1]*a[4,2]*a[0,3]*a[2,4] \
         + a[3,0]*a[1,1]*a[4,2]*a[2,3]*a[0,4] \
         + a[3,0]*a[2,1]*a[0,2]*a[1,3]*a[4,4] \
         + a[3,0]*a[2,1]*a[0,2]*a[4,3]*a[1,4] \
         + a[3,0]*a[2,1]*a[1,2]*a[0,3]*a[4,4] \
         + a[3,0]*a[2,1]*a[1,2]*a[4,3]*a[0,4] \
         + a[3,0]*a[2,1]*a[4,2]*a[0,3]*a[1,4] \
         + a[3,0]*a[2,1]*a[4,2]*a[1,3]*a[0,4] \
         + a[3,0]*a[4,1]*a[0,2]*a[1,3]*a[2,4] \
         + a[3,0]*a[4,1]*a[0,2]*a[2,3]*a[1,4] \
         + a[3,0]*a[4,1]*a[1,2]*a[0,3]*a[2,4] \
         + a[3,0]*a[4,1]*a[1,2]*a[2,3]*a[0,4] \
         + a[3,0]*a[4,1]*a[2,2]*a[0,3]*a[1,4] \
         + a[3,0]*a[4,1]*a[2,2]*a[1,3]*a[0,4] \
         + a[4,0]*a[0,1]*a[1,2]*a[2,3]*a[3,4] \
         + a[4,0]*a[0,1]*a[1,2]*a[3,3]*a[2,4] \
         + a[4,0]*a[0,1]*a[2,2]*a[1,3]*a[3,4] \
         + a[4,0]*a[0,1]*a[2,2]*a[3,3]*a[1,4] \
         + a[4,0]*a[0,1]*a[3,2]*a[1,3]*a[2,4] \
         + a[4,0]*a[0,1]*a[3,2]*a[2,3]*a[1,4] \
         + a[4,0]*a[1,1]*a[0,2]*a[2,3]*a[3,4] \
         + a[4,0]*a[1,1]*a[0,2]*a[3,3]*a[2,4] \
         + a[4,0]*a[1,1]*a[2,2]*a[0,3]*a[3,4] \
         + a[4,0]*a[1,1]*a[2,2]*a[3,3]*a[0,4] \
         + a[4,0]*a[1,1]*a[3,2]*a[0,3]*a[2,4] \
         + a[4,0]*a[1,1]*a[3,2]*a[2,3]*a[0,4] \
         + a[4,0]*a[2,1]*a[0,2]*a[1,3]*a[3,4] \
         + a[4,0]*a[2,1]*a[0,2]*a[3,3]*a[1,4] \
         + a[4,0]*a[2,1]*a[1,2]*a[0,3]*a[3,4] \
         + a[4,0]*a[2,1]*a[1,2]*a[3,3]*a[0,4] \
         + a[4,0]*a[2,1]*a[3,2]*a[0,3]*a[1,4] \
         + a[4,0]*a[2,1]*a[3,2]*a[1,3]*a[0,4] \
         + a[4,0]*a[3,1]*a[0,2]*a[1,3]*a[2,4] \
         + a[4,0]*a[3,1]*a[0,2]*a[2,3]*a[1,4] \
         + a[4,0]*a[3,1]*a[1,2]*a[0,3]*a[2,4] \
         + a[4,0]*a[3,1]*a[1,2]*a[2,3]*a[0,4] \
         + a[4,0]*a[3,1]*a[2,2]*a[0,3]*a[1,4] \
         + a[4,0]*a[3,1]*a[2,2]*a[1,3]*a[0,4]


