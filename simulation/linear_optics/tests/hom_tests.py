import numpy as np
from qy.simulation import linear_optics as lo

'''
test our code with some hom dips
'''

# build a reck scheme and a simulator
basis=lo.basis(2,2)
device=lo.lonfile('lonfiles/beamsplitter.lon')
device.draw('beamsplitter.pdf')
simulator=lo.simulator(basis, device)
simulator.set_mode('quantum')

print 'HOM DIP:'
input_state=basis.get_state('m01')
simulator.set_input_state(input_state)
noon_state=simulator.get_output_state()
print noon_state

print 'REVERSE HOM DIP:'
simulator.set_input_state(noon_state)
reverse_hom_output=simulator.get_output_state()
print reverse_hom_output

print 'TWO PHOTONS IN ONE MODE:'
input_state=basis.get_state('m00')
simulator.set_input_state(input_state)
print simulator.get_output_state()

print 'PROBABILITIES QUANTUM/CLASSICAL (HOM DIP)'
for st in ['m01', 'm00', 'm11']:
    input_state=basis.get_state(st)
    simulator.set_input_state(input_state)
    print 
    print 'INPUT:'
    print input_state
    print 'Term\tPq\t\tPc'
    for modes in basis.mode_representation:
        q=simulator.get_probability_quantum(['m']+modes)
        c=simulator.get_probability_classical(['m']+modes)
        s=','.join(map(str, modes))
        print '%s\t\t%.4f\t%.4f' % (s, q, c)

print '\nCHANGING VISIBILITY, STANDARD HOM DIP'
input_state=basis.get_state('m01')
simulator.set_input_state(input_state)
for visibility in np.linspace(0, 1, 6):
    simulator.set_visibility(visibility)
    print '\nVISIBILITY: %.3f' % visibility
    print 'Term\tPq\t\tPc'
    for modes in basis.mode_representation:
        simulator.set_mode('quantum')
        q=simulator.get_probability(['m']+modes)
        simulator.set_mode('classical')
        c=simulator.get_probability(['m']+modes)
        s=','.join(map(str, modes))
        print '%s\t\t%.4f\t%.4f' % (s, q, c)
