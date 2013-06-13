import numpy as np


def perm_ryser(A):
    ''' the permanent calculated using the ryser formula. much faster than the naive approach '''
    n,n2=A.shape
    z=np.arange(n)
    irange=xrange(2**n)
    get_index=lambda i: (i & (1 << z)) != 0 
    get_term=lambda index: ((-1)**np.sum(index))*np.prod(np.sum(A[index,:], 0))

    get_term=lambda index: np.sum(A[index,:], 0)


    indeces=map(get_index, irange)

    for index in indeces:
        print 'sum:', get_term(index)

    terms=map(get_term, indeces) 
    return np.sum(terms)*((-1)**n)

def perm_ryser_explicit(A):
    ''' the permanent calculated using the ryser formula. much faster than the naive approach '''
    n,n2=A.shape
    zrange=np.arange(n)
    irange=xrange(2**n)
    get_index=lambda i, z: (i & (1 << z)) != 0 
    get_term=lambda index: ((-1)**np.sum(index))*np.prod(np.sum(A[index,:], 0))

    total=0
    for i in irange:
        index=get_index(i, zrange)
        print index, np.sum(index)
        prefactor=(-1)**np.sum(index)
        print A[index, :].shape

        for z in range(n):
            product=1
            if get_index(i, z):
                print 'use col %d' % z
                product=product*sum

    return total*((-1)**n)

z_4x4=np.arange(4)
get_index_4x4=lambda i: (i & (1 << z_4x4)) != 0 
irange_4x4=xrange(2**4)
indeces_4x4=map(get_index_4x4, irange_4x4)

def perm_4x4(A):
    ''' faster, maybe '''
    get_term=lambda index: ((-1)**np.sum(index))*np.prod(np.sum(A[index,:], 0))
    return np.sum(map(get_term, indeces_4x4))


#def perm_ryser(A):
    #''' the permanent calculated using the ryser formula. much faster than the naive approach '''
    #n,n2=A.shape
    #z=np.arange(n)
    #y=0
    #for i in xrange(2**n):
        #index=(i & (1 << z)) != 0 
        #y+=((-1)**np.sum(index))*np.prod(np.sum(A[index,:], 0))
    #return y*((-1)**n)

