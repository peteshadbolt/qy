from scipy.misc import comb
import numpy as np
from qy.simulation import combinadics

class basis:
    def __init__(self, nphotons, nmodes):
        self.nphotons=nphotons
        self.nmodes=nmodes
        # wish we could do the below in O(1) time
        # this is very inefficient but it actually seems painful to do any other way
        # might also want to do this with generators
        print 'building basis...',
        s=lambda x: ''.join(map(str, x))

        self.hilbert_space_dimension=int(comb(nphotons+nmodes-1, nphotons,exact=1))
        self.dimensions=xrange(self.hilbert_space_dimension)

        self.mode_representation=it.combinations_with_replacement(range(self.nmodes), self.nphotons)
        self.mode_representation=map(list, self.mode_representation)
        self.mode_table=dict(zip(map(s, self.mode_representation), self.dimensions))

        self.fock_representation=map(self.mode_to_fock, self.mode_representation)
        self.fock_representation=map(list, self.fock_representation)
        self.fock_table=dict(zip(map(s, self.fock_representation), self.dimensions))
        print 'done'

    def __str__(self):
        s='Basis of %d photons in %d modes, ' % (self.nphotons, self.nmodes)
        s+='Hilbert space dimension: %d\n' % self.hilbert_space_dimension
        n=0
        for fock, mode in zip(self.fock_representation, self.mode_representation):
            s+=str(n)+'\t - \t '+ket(fock)+' \t - \t '+ket(mode)+'\n'
            n+=1
        return s+'\n'

    def mode_to_position(self, fock):
        nonzero_elements=filter(lambda x: x[1]>0, enumerate(fock))
        q=[[mode] * number for mode, number in nonzero_elements]
        return reduce(list.__add__, q)

    def mode_to_fock(self, mode):
        state=np.zeros(self.nmodes, dtype=int)
        counted=dict(Counter(mode))
        state[counted.keys()]=counted.values()
        return state.tolist()

    def fock(self, index):
        return self.fock_representation[index]

    def mode(self, index):
        return self.mode_representation[index]

    # TODO: below are mad inefficient

    def get_index(self, label):
        try:
            return int(label)
        except:
            if label[0]=='f': return self.get_index_fock(label[1:])
            if label[0]=='m': return self.get_index_mode(label[1:])

    def get_index_fock(self, label):
        label=map(int, label)
        return self.fock_table[label]
    
    def get_index_mode(self, label):
        label=map(int, label)
        label=sorted(label)
        return self.mode_table[label]

    def get_state(self, starter=None):
        new_state=state(self)
        if starter!=None: new_state.add(1, starter)
        return new_state

    def write_cache(self):
        cache_dir=os.path.join(tempfile.gettempdir(), 'qy')
        if not os.path.exists(cache_dir): os.makedirs(cache_dir)
        mode_file=open(os.path.join(cache_dir, 'basis_modes_%d_%d.p' % (self.nphotons, self.nmodes)), 'w')
        pickle.dump(self.mode_table, mode_file)
        mode_file.close()
        fock_file=open(os.path.join(cache_dir, 'basis_fock_%d_%d.p' % (self.nphotons, self.nmodes)), 'w')
        pickle.dump(self.fock_table, fock_file)
        print 'Cached basis to to %s' % cache_dir
        fock_file.close()

if __name__=='__main__':
    print 'Testing basis...'
