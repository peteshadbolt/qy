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
    cdef double norm = (-1)**n
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
    cdef double sign = 0
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
        sign=(-1)**countbits(i)
        perm_real = perm_real + sign*product_real
        perm_imag = perm_imag + sign*product_imag

    #get normalization constant
    return norm*perm_real+1j*norm*perm_imag




#def perm(cnp.ndarray[cnp.complex_t, ndim=2] A):
    #cdef int n = A.shape[0]
    #cdef double norm = (-1)**n
    #cdef int i = 0
    #cdef int z = 0
    #cdef int y = 0
    #cdef double perm_real = 0
    #cdef double perm_imag = 0
    #cdef double product_real = 0
    #cdef double product_imag = 0
    #cdef double sum_real = 0
    #cdef double sum_imag = 0
    #cdef double sign = 0
    #cdef cnp.complex_t aa

    #iterate over exponentially many terms
    #for i from 0 <= i < 2**n:
        #sign=(-1)**countbits(i)
        #product_real = 1
        #product_imag = 0

         #for each term in the index string
        #for z from 0 <= z < n:

             #if the column is marked, sum over it
            #if i & (1 << z) > 0:
                #sum_real = 0; sum_imag = 0;
                 #work over the row
                #for y from 0 <= y < n:
                    #aa = A[z,y]
                    #sum_real = sum_real+aa.real
                    #sum_imag = sum_imag+aa.imag

                #print 'sum_c:', sum_real

             #multiply the sum into the product (complex multiplication)
            #product_real = (product_real * sum_real) - (product_imag * sum_imag)
            #product_imag = (product_imag * sum_real) + (product_real * sum_imag)

         #add to the permanent
        #perm_real = perm_real + sign*product_real
        #perm_imag = perm_imag + sign*product_imag

    #get normalization constant
    #return norm*perm_real+1j*norm*perm_imag
