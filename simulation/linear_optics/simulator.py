import numpy as np
from scipy.misc import factorial
import itertools as it
from qy.simulation import permanent
from state import state

class simulator:
    '''get states and statistics from a device'''
    def __init__(self, basis, device):
        self.device=device
        self.basis=basis
        self.nmodes=self.basis.nmodes
        self.nphotons=self.basis.nphotons
        self.quantum_classical='quantum'
        self.set_perm()

    def set_perm(self, explicit=False):
        '''
        Set the permanent function that we will use from now on.
        If "explicit" is set, we will use the explicit forms up to 4x4 from now on 
        '''
        self.perm=permanent.perm_ryser
        if not explicit: return
        if self.nphotons == 2: self.perm=permanent.perm_2x2
        if self.nphotons == 3: self.perm=permanent.perm_3x3
        if self.nphotons == 4: self.perm=permanent.perm_4x4

    def get_state(self, starter=None):
        ''' get an empty state to start building with '''
        new_state=state(self.basis)
        if starter!=None: new_state.add(1, starter)
        return new_state
    
    def set_input_state(self, input_state):
        ''' set the input state in fock basis '''
        self.input_state=input_state
        modes=[self.basis.mode(index) for index in self.input_state.nonzero_terms]
        self.device.set_input_modes(modes)

    def set_mode(self, quantum_classical):
        ''' determines whether to return quantum or classical statistics '''
        if not (quantum_classical in ['quantum', 'classical']):
            print 'mode not understood!'
        self.quantum_classical=quantum_classical=='quantum'

    def map_both(self, input, output):
        ''' helper function. VERY INEFFICIENT'''
        inputs=self.basis.fock(input)
        outputs=self.basis.fock(output)
        cols=self.basis.mode(input)
        rows=self.basis.mode(output)
        return inputs, outputs, cols, rows

    def get_component(self, input, output):
        ''' get a component of the state vector '''
        inputs, outputs, cols, rows = self.map_both(input, output)
        norm=1/np.sqrt(np.product(map(factorial, inputs)+map(factorial, outputs)))
        submatrix=self.device.unitary[rows][:,cols]
        return norm*self.perm(submatrix)

    def get_single_probability_classical(self, input, output):
        ''' get a component of the state vector '''
        # this part is mega inefficient
        inputs, outputs, cols, rows = self.map_both(input, output)
        normo=np.product(map(factorial, outputs))
        norm=1/(normo)
        
        submatrix=self.device.unitary[rows][:,cols]
        submatrix=np.absolute(submatrix)
        submatrix=np.power(submatrix,2)
        submatrix=submatrix.view('complex128')
        return norm*self.perm(submatrix).real

    def get_output_state_element(self, output):
        '''get an element of the state vector, summing over terms in the input state '''
        output=self.basis.get_index(output)
        terms=[amplitude*self.get_component(input, output) for input, amplitude in self.input_state.get_nonzero_terms()]
        return np.sum(terms)

    def get_probability_quantum(self, output):
        ''' get the probability of an event '''
        amplitude=self.get_output_state_element(output) 
        return float(np.abs(amplitude))**2

    def get_probability_classical(self, output):
        ''' get the probability of an event '''
        output=self.basis.get_index(output)
        terms=[(np.abs(amplitude)**2)*self.get_single_probability_classical(input, output) for input, amplitude in self.input_state.get_nonzero_terms()]
        return float(np.sum(terms))

    def get_probability(self, output):
        ''' get the probability of an event '''
        return self.get_probability_quantum(output) if self.quantum_classical else self.get_probability_classical(output)

    def get_output_state(self, input_state=None):
        ''' compute the full state vector'''
        if input_state!=None: self.set_input_state(input_state)
        self.output_state=self.get_state()
        for output in range(self.basis.hilbert_space_dimension):
            amplitude=self.get_output_state_element(output)
            self.output_state.add_by_index(amplitude, output) 
        return self.output_state

    def __str__(self):
        '''print out'''
        s='linear optics simulator: '
        s+=str(self.device)
        return s
        
