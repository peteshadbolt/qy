from qy.simulation import linear_optics as lo
from qy import util
import itertools as it
from time import clock


def test(nphotons, nmodes, accelerate, explicit, mode='quantum'):
    '''test the simulator'''
    # build a basis, device and simulator
    basis=lo.basis(nphotons, nmodes)
    device=lo.random_unitary(basis.nmodes)
    simulator=lo.simulator(basis, device)
    simulator.configure_perm(accelerate, explicit)
    mode='quantum' if not mode else 'classical'
    simulator.set_mode(mode)

    # put photons in the top modes
    state=basis.get_state(['m'] + range(basis.nphotons))
    #print str(state).strip()
    simulator.set_input_state(state)

    # how long does it take to work over the full hilbert space
    t=clock()
    for i in range(basis.hilbert_space_dimension):
        simulator.get_probability(i)
        util.progress_bar(i/float(basis.hilbert_space_dimension-1))
    hilbert_space_time=clock()-t
    return hilbert_space_time

from matplotlib import pyplot as plt

maxp=10
photonrange = range(1,maxp)
times_cython_ryser=[[], []]
times_python_ryser=[[], []]
times_cython_explicit=[[], []]
times_python_explicit=[[], []]

for mode in 0,1:
    for nphotons in photonrange:
        print '%d photons' % nphotons
        times_python_ryser[mode].append( test(nphotons, 10, 0, 0, mode))
        times_python_explicit[mode].append( test(nphotons, 10, 0, 1, mode))
        times_cython_ryser[mode].append( test(nphotons, 10, 1, 0, mode))
        times_cython_explicit[mode].append( test(nphotons, 10, 1, 1, mode))

plt.plot(photonrange, times_python_ryser[0], '.-', label='python ryser', color='red', ms=9)
plt.plot(photonrange, times_python_explicit[0], '.-', label='python explicit', color='blue', ms=9)
plt.plot(photonrange, times_cython_ryser[0], '.-', label='cython ryser', color='#ff9900', ms=9)
plt.plot(photonrange, times_cython_explicit[0], '.-', label='cython explicit', color='#00aa00', ms=9)

plt.plot(photonrange, times_python_ryser[1], '--', color='red', ms=9, alpha=.5)
plt.plot(photonrange, times_python_explicit[1], '--', color='blue', ms=9, alpha=.5)
plt.plot(photonrange, times_cython_ryser[1], '--', color='#ff9900', ms=9, alpha=.5)
plt.plot(photonrange, times_cython_explicit[1], '--',  color='#00aa00', ms=9, alpha=.5)

plt.gca().set_yscale('log')
plt.ylabel('Time (log s)')
plt.xlabel('N photons')
plt.xticks(photonrange)
plt.legend(loc=2)
plt.grid(ls='-', color='#aaaaaa')
plt.title('10 modes, direct lookup')

plt.savefig('benchmark.pdf')
