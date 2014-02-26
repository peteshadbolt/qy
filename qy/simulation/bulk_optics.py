import numpy as np
r2=np.sqrt(2)

def hwp(phi): 
	''' a half wave plate'''
	return np.matrix([[np.cos(2*phi),np.sin(2*phi)],
                      [np.sin(2*phi), -np.cos(2*phi)]])
	
def qwp(phi): 
	''' a half wave plate'''
	return (1/r2)*np.matrix([[1+1j*np.cos(2*phi),1j*np.sin(2*phi)],
                             [1j*np.sin(2*phi), 1-1j*np.cos(2*phi)]])
