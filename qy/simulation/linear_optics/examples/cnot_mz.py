import numpy as np
from qy.simulation import linear_optics as lo

'''
Test our code with the CNOT-MZ
'''

# Build the device and a two-photon basis, draw the device
basis=lo.basis(2,2)
device=lo.beamsplitter_network(json='devices/cnot_mz.json')
device.draw('devices/cnot_mz.pdf')

# Start a simulator
simulator=lo.simulator(device, basis)

# Set the input state and get some probabilities
input_state=basis.get_state([1,3])
simulator.set_input_state(input_state)
print 'INPUT:', input_state
print 'P00', simulator.get_probability_quantum([1,3])
print 'P01', simulator.get_probability_quantum([2,3])
print 'P10', simulator.get_probability_quantum([1,4])
print 'P11', simulator.get_probability_quantum([2,4])

# Let's try a few different input states
for input_modes in [[0,1], [0,0], [1,1]]:
    input_state=basis.get_state(input_modes)
    simulator.set_input_state(input_state)
    print '\nINPUT:', str(input_state).strip()
    for index, modes in basis:
        q=simulator.get_probability_quantum(index)
        c=simulator.get_probability_classical(index)
        s=','.join(map(str, modes))
        print '%s:\tPq = %.4f\tPc = %.4f' % (s, q, c)


