import numpy as np
from scipy.misc import factorial
import itertools as it
from qy.simulation import permanent
from qy import util
from state import state

class simulator:
    '''get states and statistics from a device'''
    def __init__(self, basis, device, accelerate=True, explicit=True):
    #def __init__(self, basis, device, accelerate=True, explicit=True):
        self.device=device
        self.basis=basis
        self.nmodes=self.basis.nmodes
        self.nphotons=self.basis.nphotons
        self.visibility=1.0
        self.explicit=explicit
        self.accelerate=accelerate
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
        If "explicit" is set, we will use the explicit forms up to 4x4 from now on 
        '''
        if self.accelerate:
            if self.quantum_classical=='quantum': self.perm=permanent.perm_ryser
            if self.quantum_classical=='classical': self.perm=permanent.perm_ryser_real
            if not self.explicit: return
            if self.nphotons == 2: self.perm=permanent.perm_2x2
            if self.nphotons == 3: self.perm=permanent.perm_3x3
            if self.nphotons == 4: self.perm=permanent.perm_4x4
        else:
            self.perm=permanent.perm_ryser_p
            if not self.explicit: return
            if self.nphotons == 2: self.perm=permanent.perm_2x2_p
            if self.nphotons == 3: self.perm=permanent.perm_3x3_p
            if self.nphotons == 4: self.perm=permanent.perm_4x4_p
            if self.nphotons == 5: self.perm=permanent.perm_4x4_5

    def set_input_state(self, input_state):
        ''' set the input state in fock basis '''
        self.input_state=input_state
        modes=[self.basis.mode(index) for index in self.input_state.nonzero_terms]
        self.device.set_input_modes(modes)

    def map_both(self, input):
        ''' helper function. VERY INEFFICIENT'''
        inputs=self.basis.fock(input)
        cols=self.basis.mode(input)
        return inputs, cols

    def get_component(self, input, outputs, rows):
        ''' get a component of the state vector '''
        inputs, cols = self.map_both(input)
        norm=1/np.sqrt(np.product(map(factorial, inputs)+map(factorial, outputs)))
        submatrix=self.device.unitary[rows][:,cols]
        return norm*self.perm(submatrix)

    def get_single_probability_classical(self, input, outputs, rows):
        ''' get a component of the state vector '''
        # this part is mega inefficient
        inputs, cols = self.map_both(input)
        norm=1/np.product(map(factorial, outputs))
        submatrix=self.device.unitary[rows][:,cols]
        submatrix=np.absolute(submatrix)
        submatrix=np.power(submatrix,2)
        return norm*self.perm(submatrix).real

    def get_output_state_element(self, output):
        '''get an element of the state vector, summing over terms in the input state '''
        output=self.basis.get_index(output)
        outputs=self.basis.fock(output)
        rows=self.basis.mode(output)
        terms=[amplitude*self.get_component(input, outputs, rows) for input, amplitude in self.input_state.get_nonzero_terms()]
        return np.sum(terms)

    def get_probability_quantum(self, output):
        ''' get the probability of an event '''
        amplitude=self.get_output_state_element(output) 
        return float(np.abs(amplitude))**2

    def get_probability_classical(self, output):
        ''' get the probability of an event '''
        output=self.basis.get_index(output)
        outputs=self.basis.fock(output)
        rows=self.basis.mode(output)
        terms=[(np.abs(amplitude)**2)*self.get_single_probability_classical(input, outputs, rows) for input, amplitude in self.input_state.get_nonzero_terms()]
        return float(np.sum(terms))
    
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
            probabilities[tuple(pattern)]=self.get_probability(pattern)
            util.progress_bar(index, len(patterns))
        return util.dict_to_sorted_numpy(probabilities)

    def from_basis(self):
        ''' generate all probabilities relevant to a given detection model'''
        probabilities={}
        for index in range(self.basis.hilbert_space_dimension):
            modes=self.basis.mode(index)
            probabilities[tuple(modes)]=self.get_probability(index)
            util.progress_bar(index, self.basis.hilbert_space_dimension)
        return util.dict_to_sorted_numpy(probabilities)

    def __str__(self):
        '''print out'''
        s='linear optics simulator: '
        s+=str(self.device)
        return s
        
