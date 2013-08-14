import numpy as np
from scipy.misc import factorial
import itertools as it
from qy.simulation import permanent
from qy import util
from state import state
from basis import basis

class simulator:
    ''' Get states and statistics from a device '''
    def __init__(self, device, new_basis=None, nphotons=None):
        self.device=device
        self.basis=new_basis
        self.nmodes=self.basis.nmodes
        self.nphotons=self.basis.nphotons
        self.visibility=1.0
        self.set_mode('quantum')

    def set_visibility(self, new_visibility):
        ''' Set the visibility of quantum interference '''
        self.visibility=new_visibility
        self.set_mode(self.quantum_classical)

    def set_mode(self, quantum_classical):
        ''' Determines whether to return quantum or classical statistics '''
        self.quantum_classical=quantum_classical
        if self.quantum_classical=='quantum':
            pass
        else: 
            pass
        self.set_perm()

    def set_perm(self):
        ''' Make the best choice of permanent function we can '''
        if self.quantum_classical=='quantum': self.perm=permanent.perm_ryser
        if self.quantum_classical=='classical': self.perm=permanent.perm_ryser_real
        if self.nphotons == 2: self.perm=permanent.perm_2x2
        if self.nphotons == 3: self.perm=permanent.perm_3x3
        if self.nphotons == 4: self.perm=permanent.perm_4x4

    def set_input_state(self, input_state):
        ''' Set the input state '''
        self.input_state=input_state
        modes=[self.basis.get_modes(term) for term in input_state.nonzero_terms]
        self.device.set_input_modes(modes)

    def get_probability_quantum(self, pattern):
        ''' Get a single probability '''
        pass

    def get_probability_classical(self, pattern):
        ''' Get a single probability '''
        pass

    def get_probabilities_quantum(self, outputs=None):
        ''' Iterate over a bunch of patterns. Optimized for sparse input states'''
        if outputs==None: outputs=xrange(self.basis.hilbert_space_dimension)
        try:
            outputs=map(self.basis.from_modes, outputs)
        except TypeError:
            pass
        N=len(outputs)
        amplitudes=np.zeros(N, dtype=complex)

        for input in self.input_state.nonzero_terms:
            cols=self.basis.get_modes(input)
            n1=self.basis.get_normalization_constant(cols)
            for index, output in enumerate(outputs):
                rows=self.basis.get_modes(output)
                n2=self.basis.get_normalization_constant(rows)
                term=self.perm(self.device.unitary[rows][:,cols])/np.sqrt(n1*n2)
                amplitudes[index]+=term
                util.progress_bar(index, N)

        amplitudes=np.abs(amplitudes)
        amplitudes=amplitudes*amplitudes
        return amplitudes

    def get_probabilities(self, **kwargs):
        '''
        '''

    def __str__(self):
        ''' Print out '''
        s='Linear optics simulator: '
        s+=str(self.device)
        return s

if __name__=='__main__':
    from random_unitary import random_unitary
    p=6
    m=p**2
    basis=basis(p, m)

    for 


    device=random_unitary(m)
    simulator=simulator(device, basis)
    state=simulator.basis.get_state(range(p))
    simulator.set_input_state(state)
    
    #device=random_unitary(m)
    #simulator=simulator(device, new_basis=basis)
    #state=simulator.basis.get_state(range(p))
    #simulator.set_input_state(state)
    #simulator.context_free()

    #def get_probability_limited_visibility(self, output):
        #''' Get a probability with limited visibility of quantum interference '''
        #q=self.get_probability_quantum(output)
        #c=self.get_probability_classical(output)
        #return self.visibility*q+(1-self.visibility)*c



    #def get_single_probability_classical(self, input, rows, norm):
        #''' Get a component of the state vector '''
        #cols=self.basis.get_modes(input)
        #submatrix=self.device.unitary[rows][:,cols]
        #submatrix=np.power(np.absolute(submatrix).real,2)
        #return norm*self.perm(submatrix).real

    #def get_probability_classical(self, output):
        #''' Get the probability of an event '''
        #rows=self.basis.get_modes(output)
        #norm=1/self.basis.get_normalization_constant(rows)
        #terms=[(np.abs(self.input_state.vector[input])**2)*self.get_single_probability_classical(input, rows, norm) for input, in self.input_state.nonzero_terms)]
        #return float(np.sum(terms))


    #def get_component(self, input, rows, norm):
        #''' Get a component of the state vector '''
        #cols=self.basis.get_modes(input)
        #n1=self.basis.get_normalization_constant(cols)
        #norm=1/np.sqrt(n1*norm)
        #submatrix=self.device.unitary[rows][:,cols]
        #return norm*self.perm(submatrix)




    #def get_output_state_element(self, output):
        #'''Get an element of the state vector, summing over terms in the input state '''
        #rows=self.basis.get_modes(output)
        #norm=self.basis.get_normalization_constant(rows)
        #terms=[amplitude*self.get_component(input, rows, norm) for input, amplitude in self.input_state.get_nonzero_terms()]
        #return np.sum(terms)

    #def get_output_state(self, input_state=None):
        #''' Compute the full state vector'''
        #if input_state!=None: self.set_input_state(input_state)
        #self.output_state=self.basis.get_state()
        #for output in range(self.basis.hilbert_space_dimension):
            #amplitude=self.get_output_state_element(output)
            #self.output_state.add_by_index(amplitude, output) 
        #return self.output_state

