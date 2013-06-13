import numpy as np
from numpy.linalg import qr
import perm

# generate a test matrix
def get_random_u(size):
    real=np.random.normal(0, 1, [size, size])
    imag=1j*np.random.normal(0, 1, [size, size])
    test_unitary=real+imag
    test_unitary, r = qr(test_unitary)
    return test_unitary

size=5
u=get_random_u(size)
print u.dtype
print perm.perm_ryser(u)
