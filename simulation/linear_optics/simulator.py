import numpy as np
import itertools as it
from qy.simulation import permanent
from qy import util
from state import state
from basis import basis

class simulator:
    ''' Get states and statistics from a device '''
    def __init__(self, device, new_basis=None, nphotons=None):
        self.device=device
        if new_basis==None:
            self.basis=basis(device.nmodes, nphotons)
        else:
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
        if isinstance(input_state, list): input_state=self.basis.get_state(input_state)
        self.input_state=input_state
        modes=[self.basis.modes_from_index(term) for term in input_state.nonzero_terms]
        self.device.set_input_modes(modes)

    def get_probabilities_quantum(self, outputs=None):
        ''' Iterate over a bunch of patterns.  Outputs must be a list or generator of indeces '''
        N=len(outputs)
        amplitudes=np.zeros(N, dtype=complex)
        for input_index, input_amplitude in self.input_state:
            cols=self.basis(input_index)
            n1=self.basis.get_normalization_constant(cols)
            for index, output in enumerate(outputs):
                rows=self.basis.modes_from_index(output)
                n2=self.basis.get_normalization_constant(rows)
                amplitudes[index]+=self.perm(self.device.unitary[rows][:,cols])/np.sqrt(n1*n2)
                util.progress_bar(index, N, label='Computing probabilities...')
        probabilities=np.abs(amplitudes)
        probabilities=probabilities*probabilities
        return probabilities

    def get_probabilities_classical(self, outputs=None):
        ''' Iterate over a bunch of patterns.  Outputs must be a list or generator of indeces '''
        N=len(outputs)
        probabilities=np.zeros(N, dtype=float)
        for input in self.input_state.nonzero_terms:
            cols=self.basis.modes_from_index(input)
            for index, output in enumerate(outputs):
                rows=self.basis.modes_from_index(output)
                n2=self.basis.get_normalization_constant(rows)
                submatrix=np.abs(self.device.unitary[rows][:,cols])
                submatrix=np.multiply(submatrix, submatrix)
                probabilities[index]+=self.perm(submatrix)/n2
                util.progress_bar(index, N, label='Computing probabilities...')
        return probabilities

    def get_probabilities_limited_visibility(self, outputs=None):
        ''' Simulate limited dip visibility '''
        self.set_mode('quantum')
        q=self.get_probabilities_quantum(outputs)
        self.set_mode('classical')
        c=self.get_probabilities_classical(outputs)
        self.set_mode('quantum')
        return self.visibility*q+(1-self.visibility)*c

    def get_probabilities(self, **kwargs):
        ''' Helpful interface to getting probabilities '''
        # Get the list of output modes in a sensible format
        outputs=kwargs['patterns'] if 'patterns' in kwargs else xrange(self.basis.hilbert_space_dimension)
        try:
            outputs=map(self.basis.modes_to_index, outputs)
        except TypeError:
            pass

        # Helpful: check that the device has had its unitary calculated
        if self.device.unitary==None: self.device.get_unitary()

        # Compute all the probabilities 
        probabilities=None
        if self.quantum_classical=='quantum':
            if self.visibility==1:
                probabilities=self.get_probabilities_quantum(outputs)
            else:
                probabilities=self.get_probabilities_limited_visibility(outputs)
        elif self.quantum_classical=='classical':
            probabilities=self.get_probabilities_classical(outputs)

        # Should we label?
        label = kwargs['label'] if 'label' in kwargs else False
        if not label: return probabilities

        # Label the list of probabilities and make sure that it is sorted
        d={}
        for index, output in enumerate(outputs):
            label=tuple(self.basis.modes_from_index(output))
            d[label]=probabilities[index]
            util.progress_bar(index, len(outputs), label='Labelling...')
        return util.dict_to_sorted_numpy(d)

    def get_probability_quantum(self, pattern):
        ''' Get a single probability. Do not use this in big loops! '''
        self.set_mode('quantum')
        return float(self.get_probabilities(patterns=[pattern], label=False))

    def get_probability_classical(self, pattern):
        ''' Get a single probability. Do not use this in big loops! '''
        self.set_mode('classical')
        return float(self.get_probabilities(patterns=[pattern], label=False))

    def __str__(self):
        ''' Print out '''
        s='Linear optics simulator: '
        s+=str(self.device)
        s+=str(self.basis)
        return s

if __name__=='__main__':
    ''' Test out the simulator '''
    from beamsplitter_network import beamsplitter_network

    # Make a beamsplitter device
    device=beamsplitter_network(2)
    device.add_beamsplitter(0,0)

    # Make a simulator and set the input state
    simulator=simulator(device, nphotons=2)
    simulator.set_input_state([0,0])
    print '\nSimulator summary:'
    print simulator
    print '\nInput state:'
    print simulator.input_state

    # Get some probabilities
    print simulator.get_probabilities()
    print simulator.get_probabilities(label=True)
    print simulator.get_probabilities(patterns=[[0,0]])

