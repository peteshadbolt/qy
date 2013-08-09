import numpy as np
from scipy.misc import factorial
import itertools as it
from qy.simulation import permanent
from qy import util
from state import state
from basis import basis

class simulator:
    '''get states and statistics from a device'''
    def __init__(self, device, new_basis=None, nphotons=None):
        self.device=device
        if new_basis!=None: self.basis=new_basis
        if nphotons!=None: self.basis=basis(nphotons, self.device.nmodes)
        self.nmodes=self.basis.nmodes
        self.nphotons=self.basis.nphotons
        self.visibility=1.0
        self.set_mode('quantum')

    def set_visibility(self, new_visibility):
        ''' set the visibility of quantum interference '''
        self.visibility=new_visibility
        self.set_mode(self.quantum_classical)

    def set_mode(self, quantum_classical):
        ''' determines whether to return quantum or classical statistics '''
        if not (quantum_classical in ['quantum', 'classical']): print 'Quantum/classical mode not understood!'; return
        self.quantum_classical=quantum_classical

        # choose the function that we will use to compute probabilities
        if self.quantum_classical=='quantum':
            if self.visibility==1:
                self.get_probability = self.get_probability_quantum
            else:
                self.get_probability = self.get_probability_limited_visibility
        else: 
            self.get_probability = self.get_probability_classical

        # re-select the function that we'll use to compute permanents
        self.set_perm()

    def set_perm(self):
        '''
        Make the best choice of permanent function we can
        '''
        if self.quantum_classical=='quantum': self.perm=permanent.perm_ryser
        if self.quantum_classical=='classical': self.perm=permanent.perm_ryser_real
        if self.nphotons == 2: self.perm=permanent.perm_2x2
        if self.nphotons == 3: self.perm=permanent.perm_3x3
        if self.nphotons == 4: self.perm=permanent.perm_4x4

    def set_input_state(self, input_state):
        ''' set the input state '''
        self.input_state=input_state
        modes=[self.basis.get_modes(x) for x in input_state.nonzero_terms]
        self.device.set_input_modes(modes)

    def get_component(self, input, rows, norm):
        ''' get a component of the state vector '''
        cols=self.basis.get_modes(input)
        n1=self.basis.get_normalization_constant(cols)
        norm=1/np.sqrt(n1*norm)
        submatrix=self.device.unitary[rows][:,cols]
        return norm*self.perm(submatrix)

    def get_single_probability_classical(self, input, rows, norm):
        ''' get a component of the state vector '''
        cols=self.basis.get_modes(input)
        submatrix=self.device.unitary[rows][:,cols]
        submatrix=np.power(np.absolute(submatrix).real,2)
        return norm*self.perm(submatrix).real

    def get_output_state_element(self, output):
        '''get an element of the state vector, summing over terms in the input state '''
        rows=self.basis.get_modes(output)
        norm=self.basis.get_normalization_constant(rows)
        terms=[amplitude*self.get_component(input, rows, norm) for input, amplitude in self.input_state.get_nonzero_terms()]
        return np.sum(terms)

    def get_probability_classical(self, output):
        ''' get the probability of an event '''
        rows=self.basis.get_modes(output)
        norm=1/self.basis.get_normalization_constant(rows)
        terms=[(np.abs(amplitude)**2)*self.get_single_probability_classical(input, rows, norm) for input, amplitude in self.input_state.get_nonzero_terms()]
        return float(np.sum(terms))

    def get_probability_quantum(self, output):
        ''' get the probability of an event '''
        amplitude=self.get_output_state_element(output) 
        return float(np.abs(amplitude))**2
    
    def get_probability_limited_visibility(self, output):
        ''' get a probability with limited visibility of quantum interference '''
        q=self.get_probability_quantum(output)
        c=self.get_probability_classical(output)
        return self.visibility*q+(1-self.visibility)*c

    def get_output_state(self, input_state=None):
        ''' compute the full state vector'''
        if input_state!=None: self.set_input_state(input_state)
        self.output_state=self.basis.get_state()
        for output in range(self.basis.hilbert_space_dimension):
            amplitude=self.get_output_state_element(output)
            self.output_state.add_by_index(amplitude, output) 
        return self.output_state

    def from_pattern_list(self, patterns):
        ''' generate all probabilities, iterating over a list of patterns'''
        probabilities={}
        for index, pattern in enumerate(patterns):
            probabilities[tuple(pattern)]=self.get_probability(index)
            util.progress_bar(index, len(patterns))
        return util.dict_to_sorted_numpy(probabilities)

    def from_basis(self):
        ''' generate all probabilities relevant to a given detection model'''
        probabilities={}
        for index in range(self.basis.hilbert_space_dimension):
            modes=self.basis.get_modes(index)
            probabilities[tuple(modes)]=self.get_probability(index)
            util.progress_bar(index, self.basis.hilbert_space_dimension)
        return util.dict_to_sorted_numpy(probabilities)

    def context_free(self):
        ''' generate all probabilities relevant to a given detection model, without any context'''
        probabilities=np.zeros(self.basis.hilbert_space_dimension)
        for index in range(self.basis.hilbert_space_dimension):
            probabilities[index]=self.get_probability(index)
            util.progress_bar(index, self.basis.hilbert_space_dimension)
        return probabilities

    def __str__(self):
        '''print out'''
        s='linear optics simulator: '
        s+=str(self.device)
        return s

if __name__=='__main__':
    from random_unitary import random_unitary
    p=6
    m=p**2
    basis=basis(p, m)
    device=random_unitary(m)
    simulator=simulator(device, new_basis=basis)
    state=simulator.basis.get_state(range(p))
    simulator.set_input_state(state)
    simulator.context_free()


