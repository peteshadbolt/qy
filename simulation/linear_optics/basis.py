from qy.simulation import combinadics
from misc import ket
from state import state

class basis:
    def __init__(self, nphotons, nmodes):
        self.nphotons=nphotons
        self.nmodes=nmodes
        self.hilbert_space_dimension=combinadics.choose(self.nphotons+self.nmodes-1, self.nphotons)
        self.iterator_index=0

    def get_state(self, starter=None):
        ''' Get a new state in this basis '''
        new_state=state(self)
        if starter!=None: new_state.add(1, starter)
        return new_state

    def modes_from_index(self, index):
        ''' Given an index, return the modes that the photons are in '''
        return combinadics.from_index(index, self.nphotons, self.nmodes)

    def modes_to_index(self, modes):
        ''' Given a list of modes, return the index of that term '''
        return combinadics.to_index(modes, self.nphotons, self.nmodes)

    def get_normalization_constant(self, modes):
        ''' Given an index, return the normalization constant '''
        return combinadics.get_normalization(modes)

    def __iter__(self):
        ''' Allow use as an iterator '''
        return self

    def next(self):
        ''' Allow use as an iterator '''
        if self.iterator_index < self.hilbert_space_dimension:
            cur, self.iterator_index = self.iterator_index, self.iterator_index+1
            return cur, self.modes_from_index(cur)
        else:
            self.iterator_index=0
            raise StopIteration()

    def __str__(self):
        s='Basis of %d photons in %d modes, ' % (self.nphotons, self.nmodes)
        s+='Hilbert space dimension: %d\n' % self.hilbert_space_dimension
        for index in xrange(self.hilbert_space_dimension):
           s+=str(index)+'\t - \t '+ket(self.modes_from_index(index))+'\n'
        return s

if __name__=='__main__':
    print 'Testing basis...'
    b=basis(2,4)
    print b
    print b.get_normalization_constant(b.modes_from_index(7))
    print b.get_state([1,2])
    for x in b:
        print x
