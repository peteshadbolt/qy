import numpy as np
from qy.simulation import linear_optics as lo

# First Let's load up a device from a JSON definition file:
device=lo.beamsplitter_network(json='devices/cnot_mz.json')
print device
print device.get_unitary().round(2)
print device.nmodes

# Draw the waveguide structure as a PDF file
device.draw('devices/cnot_mz.pdf')

# Now let's make a simulator, and link it to the device
simulator=lo.simulator(device, nphotons=2)

# Let's have a look at the basis
print simulator.basis

# Set the input state to two photons in the top mode, and look at 
# the output probabilities and output state
simulator.set_input_state([0, 0])
print simulator.input_state
print simulator.get_probabilities().round(2)
print simulator.get_output_state()

# Superposition input states, and classical statistics
state=simulator.basis.get_state()
state[0,1]=1/np.sqrt(2)
state[3,4]=1/np.sqrt(2)
print state
simulator.set_input_state(state)
simulator.set_visibility(0.5)
print simulator.get_probabilities()

# Now let's test the speed/performance of the code. 
# Let's do 4 photons in 16 modes of a Haar-random U
# Hilbert space dimension is now 3876
device=lo.random_unitary(16)
simulator=lo.simulator(device, nphotons=4)
simulator.set_input_state(range(4))  # Photons go in the top 4 modes
probs=simulator.get_probabilities(label=True)

