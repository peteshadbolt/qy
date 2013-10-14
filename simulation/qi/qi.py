import numpy as np
from scipy.linalg import sqrtm

# bloch sphere
r2=np.sqrt(2)
zero=np.matrix([[1],[0]])
one=np.matrix([[0],[1]])
plus=(zero+one)/r2
minus=(zero-one)/r2
plusi=(zero+1j*one)/r2
minusi=(zero-1j*one)/r2

# one-qubit gates, paulis
identity  = np.matrix([[1,0],[0,1]])
px = np.matrix([[0,1],[1,0]])
py = np.matrix([[0,-1j],[1j,0]])
pz = np.matrix([[1,0],[0,-1]])
hadamard = np.matrix([[1,1],[1,-1]])/r2
dc = np.matrix([[1,1j],[1j,1]])/r2
paulis=[px,py,pz]
pauli_dict={x:p for x, p in zip('xyz', paulis)}
tomography=[identity,px,py,pz]
def phase(phi):
    ''' a phase gate '''
    return np.matrix([[1,0],[0,np.exp(phi*1j)]])

# two-qubit states
psi_plus=(np.kron(zero,one)+np.kron(one,zero))/r2
psi_minus=(np.kron(zero,one)-np.kron(one,zero))/r2
phi_plus=(np.kron(zero,zero)+np.kron(one,one))/r2
phi_minus=(np.kron(zero,zero)-np.kron(one,one))/r2

# two-qubit gates
cnot=np.matrix([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
cz=np.matrix([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]])

# krauss operators
krauss=[]
for a in paulis:
	for b in paulis:
		krauss.append(np.kron(a,b))
kraussh=[k.H for k in krauss]

def braket(a,b): 
	''' <a|b> '''
	return a.H*b
	
def ketbra(a,b): 
	''' |a><b| '''
	return np.matrix(np.outer(a,b.H))
	
def orth(a,b): 
	''' determine whether two state vectors are orthogonal '''
	return np.abs(np.trace(a.T*b))<0.000001

def density_matrix(psi): 
	''' convert a state vector to a density matrix '''
	return np.matrix(np.outer(psi,psi.H))

def probability(a,b): 
	''' the probability of finding the system in state a given state b '''
	return np.abs(braket(a,b))**2
overlap=probability

def eigenvectors(m): 
	''' get the eigenvectors of a matrix '''
	return np.linalg.eigh(m)[1]

def check_hermitian(x): 
	''' check if a matrix is hermitian '''
	return np.allclose(x, x.H)

def check_positive_semidefinite(x): 
	''' check if an operator is positive semidefinite '''
	vals, vecs = np.linalg.eig(x)
	tol=-0.0000001
	return all([x.real>tol and x.imag>tol for x in vals])

def check_physical(chi):
    ''' checks that a density matrix is physical '''
    if check_hermitian(chi):
        if check_positive_semidefinite(chi):
            if abs(1-np.trace(chi).real) < 1.0/1e9:
                return True
    return False

def mixed_mixed_fidelity(rho,sigma):
	''' quantum state fidelity between mixed states as defined by paul kwiat '''	
	print 'computing fidelity between two mixed states...'
	x=np.matrix(sqrtm(rho))
	return np.trace(sqrtm(x*sigma*x)).real**2
	
def pure_pure_fidelity(psi, phi):
	return float(abs(braket(psi,phi))**2)

def mixed_pure_fidelity(rho,target):
	''' quantum state fidelity between a pure state and a mixed state [kwiat]'''	
	return float((target.H*rho*target).real)
	
def fidelity(a, b):
	''' quantum state fidelity between two states. 
	guesses whether these are expressed as density matrices or state vectors '''
	aw,ah=a.shape
	a_type='m' if aw==ah else 'v'
	bw,bh=b.shape
	b_type='m' if bw==bh else 'v'
	if a_type=='m' and b_type=='m': return mixed_mixed_fidelity(a,b)
	if a_type=='m' and b_type=='v': return mixed_pure_fidelity(a,b)
	if a_type=='v' and b_type=='m': return mixed_pure_fidelity(b,a)
	if a_type=='v' and b_type=='v': return pure_pure_fidelity(a,b)
