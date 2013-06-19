import numpy as np
import qi

def ph(phi): 
	''' a phase shifter on two modes '''
	return np.matrix([[1,0],[0,np.exp(1j*phi)]])

def vector_state(index, nqubits):
	''' get the state vector from a number. e.g. (0,2)-> |00>, (3,2) -> |11> '''
	name = str(bin(index))[2:]
	name = ('0'*(nqubits-len(name))+name)
	psi=np.zeros(2**nqubits)
	psi[index]=1
	return name, np.matrix(psi).T

def cu_gate(unitary, control_qubit, target_qubit, nqubits):
	''' generate a CU gate unitary'''
	d=2**nqubits
	cu=np.matrix(np.zeros((d,d)), dtype=complex)
	extended_u=[unitary if i==target_qubit else qi.identity for i in range(nqubits)]
	extended_u=reduce(np.kron, extended_u)	
	for bit in range(d):
		name, state=vector_state(bit, nqubits)
		cu+=qi.ketbra(state, state) if name[control_qubit]=='0' else qi.ketbra(extended_u*state, state)
	return cu

def cnot_gate(control_qubit, target_qubit, nqubits):
    ''' a cnot gate '''
    return cu_gate(qi.pz, control_qubit, target_qubit, nqubits)
	
def swap_gate(qubit_1, qubit_2, nqubits):
	''' generate a SWAP gate unitary '''
	d=2**nqubits
	swap=np.matrix(np.zeros((d,d)), dtype=complex)
	for bit in range(d):
		name, state=vector_state(bit, nqubits)
		name_swapped=list(name)
		name_swapped[qubit_1]=name[qubit_2]
		name_swapped[qubit_2]=name[qubit_1]
		newstate=reduce(np.kron, map(lambda x: qi.zero if x=='0' else qi.one, name_swapped))
		swap+=qi.ketbra(newstate, state)
	return swap
	
def reverse_qubit_order(nqubits):
	''' reverse the qubit order using SWAP gates '''
	d=2**nqubits
	unitary=np.matrix(np.eye(d,d), dtype=np.complex)
	for i in range(int(np.floor(nqubits/2.))):
		unitary=swap_gate(i, nqubits-1-i, nqubits)*unitary
	return unitary

def r_gate(k):
	''' R as defined in Nielsen and Chuang 5.1: the quantum fourier transform '''
	return np.matrix([[  1,			0			],
				   [  0,	np.exp(2*np.pi*1j/(2**k))	]])

def cr_gate(k, control_qubit, target_qubit, nqubits):
	''' controlled version of the R gate'''
	return cu_gate(r_gate(k), control_qubit, target_qubit, nqubits)
	
def indexed_hadamard_gate(qubit, nqubits):
	''' a hadamard on a particular qubit '''
	return reduce(np.kron, [qi.hadamard if i==qubit else qi.identity for i in range(nqubits)])

def indexed_phase_gate(qubit, phi, nqubits):
	''' a phase on a particular qubit '''
	return reduce(np.kron, [qi.phase(phi) if i==qubit else qi.identity for i in range(nqubits)])
	
def qft_first_stage(nqubits):
	''' first stage of the qft '''
	d=2**nqubits
	unitary=np.matrix(np.eye(d,d), dtype=np.complex)
	for working_qubit in range(nqubits):
		unitary=indexed_hadamard(working_qubit, nqubits)*unitary
		for i in range(1, nqubits-working_qubit):
			target_qubit=i+working_qubit
			unitary=cr_gate(i+1, working_qubit, target_qubit, nqubits)*unitary
	return unitary
	
def quantum_fourier_transform(nqubits):
	''' quantum fourier transform, per Nielsen and Chuang fig 5.1 '''
	unitary=qft_first_stage(nqubits)
	unitary=reverse_qubit_order(nqubits)*unitary
	return unitary
