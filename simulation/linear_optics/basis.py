from scipy.misc import comb
import numpy as np
from qy.simulation import combinadics
import itertools as it
from collections import Counter

def ket(term): return '|%s>' % (''.join(map(str, term)))

class basis:
    def __init__(self, nphotons, nmodes):
        self.nphotons=nphotons
        self.nmodes=nmodes
        self.hilbert_space_dimension=combinadics.choose(self.nphotons+self.nmodes-1, self.nphotons)

    def __str__(self):
        s='Basis of %d photons in %d modes, ' % (self.nphotons, self.nmodes)
        s+='Hilbert space dimension: %d\n' % self.hilbert_space_dimension
        for index in xrange(self.hilbert_space_dimension):
            modes=combinadics.from_index(index, self.nphotons, self.nmodes)
            s+=str(index)+'\t - \t '+ket(modes)+'\n'
        return s+'\n'

    def get_state(self, starter=None):
        new_state=state(self)
        if starter!=None: new_state.add(1, starter)
        return new_state

if __name__=='__main__':
    print 'Testing basis...'
    b=basis(2,4)
    print b
