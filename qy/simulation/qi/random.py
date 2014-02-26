from numpy import *
from numpy.random import randn
from numpy.linalg import qr

def random_unitary_haar(n):
	""" 
	Returns a U(n) unitary of size n - random by the Haar measure
	Taken from "How to generate random matrices from the classical compact groups" (Francesco Mezzadri)
	"""
	z = (randn(n,n) + 1j*randn(n,n))/sqrt(2.0)
	q,r = linalg.qr(z)
	d = diagonal(r)
	ph = d/absolute(d)
	q = multiply(q,ph,q)
	return matrix(q)
	
def random_matrix_ginibre(n):
	""" 
	Returns a matrix of size n according to the Ginibre ensemble
	"""
	return matrix((randn(n,n) + 1j*randn(n,n))/sqrt(2.0))
	
def random_denisty_matrix_bures(n):
	"""
	Returns a density matrix random by the Bures ensemble
	"""
	G=random_matrix_ginibre(n)
	U=random_unitary_haar(n)
	a=(ones((n,n), complex)+U)*G*G.H*(ones((n,n), complex)+U.H)
	return a/trace(a)
	
def random_denisty_matrix_hilbert_schmidt(n):
	"""
	Returns a density matrix random by the Bures ensemble
	"""
	G=random_matrix_ginibre(n)
	a=G*G.H
	return a/trace(a)