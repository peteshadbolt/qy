from qy.simulation import combinadics
from state import state

def ket(term): return '|%s>' % (''.join(map(str, term)))

class basis:
    def __init__(self, nphotons, nmodes):
        ''' A fast basis for P photons in M modes '''
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

    ######## BOILERPLATE ########

    def __str__(self):
        s='Basis of %d photons in %d modes, ' % (self.nphotons, self.nmodes)
        s+='Hilbert space dimension: %d\n' % self.hilbert_space_dimension
        if self.hilbert_space_dimension<200:
           s+='\n'.join([str(index)+'\t - \t '+ket(modes) for index, modes in self])
        return s

    def __len__(self):
        ''' Number of elements in the basis '''
        return self.hilbert_space_dimension

    def __getitem__(self, key):
        ''' Allow basic square-bracket indexing '''
        if isinstance(key, int):
            if key<0: key+=self.hilbert_space_dimension
            if key>=self.hilbert_space_dimension: raise IndexError, 'The index (%d) is out of range' % key
            return self.modes_from_index(key)
        elif isinstance(key, list) or isinstance(key, tuple):
            return self.modes_to_index(key)
        else:
            raise TypeError, 'Invalid basis index'

    def __iter__(self): return self
    def next(self):
        ''' Allow use as an iterator (for index, modes in basis)'''
        if self.iterator_index < self.hilbert_space_dimension:
            cur, self.iterator_index = self.iterator_index, self.iterator_index+1
            return cur, self.modes_from_index(cur)
        else:
            self.iterator_index=0
            raise StopIteration()

if __name__=='__main__':
    ''' Test out the basis class '''
    b=basis(2,3)

    print b
    print 'Zeroth element is this: ', b[0]
    print 'Normalization constant: ', b.get_normalization_constant(b.modes_from_index(3))
    print 'State [1,2]: '
    print b.get_state([1,2])
    print b[0]
    print b[0,2]
    print 'Testing iteration:'
    for x in b:
        print x
