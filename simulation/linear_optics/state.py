import numpy as np
from misc import ket

class state:
    def __init__(self, basis):
        self.nphotons=basis.nphotons
        self.nmodes=basis.nmodes
        self.basis=basis
        self.tolerance=0.00001
        self.nonzero_terms=set()
        self.vector=np.zeros(self.basis.hilbert_space_dimension, dtype=complex)

    def check_normalization(self):
        '''check that the state is normalized'''
        total=np.sum(np.abs(self.vector)**2)
        if np.abs(total-1)>self.tolerance: print 'Warning: State is not normalized'
        return total

    def normalize(self):
        '''docstring for normalize'''
        print 'Warning: You are using a dodgy normalization technique'
        total=np.sum(np.abs(self.vector)**2)
        self.vector*=1/np.sqrt(total)
    
    def get_matrix(self):
        ''' return the state vector as a numpy matrix '''
        return np.matrix(self.vector).T

    def get_nonzero_terms(self):
        ''' return a list of nonzero probability amplitudes and corresponding indeces '''
        return zip(self.nonzero_terms, self.vector[list(self.nonzero_terms)])

    def add(self, probability_amplitude, label):
        ''' add a term '''
        index=self.basis.from_modes(label)
        if np.abs(probability_amplitude)>=self.tolerance: self.nonzero_terms.add(index)
        self.vector[index]+=probability_amplitude

    def add_by_index(self, probability_amplitude, index):
        ''' add a term '''
        if np.abs(probability_amplitude)>=self.tolerance: self.nonzero_terms.add(index)
        self.vector[index]+=probability_amplitude

    def __str__(self):
        s=''
        if len(self.nonzero_terms)==0: s+='No nonzero terms (a "blank" state)'
        self.nonzero_terms=sorted(self.nonzero_terms)
        for index in self.nonzero_terms:
            a=self.vector[index]
            s+='%.2f + %.2fi  ' % (a.real, a.imag)
            if self.nmodes<10: s+='  ('+ket(self.basis.get_modes(index))+')'
            s+='\n'
        return s
    
