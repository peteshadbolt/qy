import numpy as np
from qy.simulation import linear_optics as lo

'''
Test our code with some HOM dips
'''

# Build a BS and a two-photon basis
basis=lo.basis(2,2)
device=lo.beamsplitter_network(json='devices/beamsplitter.json')

# Draw it
device.draw('devices/beamsplitter.pdf')

# Start a simulator
simulator=lo.simulator(device, basis)

# Set the input state and get some probabilities
input_state=basis.get_state([0,1])
print 'INPUT:', input_state
simulator.set_input_state(input_state)
print simulator.get_probability_quantum([0,0])
print simulator.get_probability_quantum([0,1])
print simulator.get_probability_classical([0,1])


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


