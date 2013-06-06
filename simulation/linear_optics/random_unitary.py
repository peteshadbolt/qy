import numpy as np
from numpy.linalg import qr
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import rc 
rc('font', family='arial', size=8)

def sym(w): return w.dot(inv(sqrtm(w.T.dot(w))))

class random_unitary:
    '''just gets a random unitary'''
    def __init__(self, nmodes):
        self.nmodes = nmodes
        self.name='random unitary'
        self.input_modes=[]
        self.get_unitary()

    def get_ndof(self):
        '''get the number of degrees of freedom'''
        return 0

    def set_input_modes(self, mode_list):
        ''' set the input modes '''
        self.input_modes=mode_list

    def set_parameters(self, p):
        ''' set all parameters'''
        pass

    def get_unitary(self):
        ''' build the unitary '''
        real=np.random.normal(0, 1, [self.nmodes, self.nmodes])
        imag=1j*np.random.normal(0, 1, [self.nmodes, self.nmodes])
        self.unitary=real+imag
        self.unitary, r = qr(self.unitary)
        return self.unitary
    
    def __str__(self):
        ''' make a string representing the beamsplitter network '''
        s='%d-mode %s\n' % (self.nmodes, self.name)
        return s

    def draw(self, filename='figures/out.pdf'):
        ''' draw the thing '''
        pass

if __name__=='__main__':
    q=random_unitary(5)
    print q
    print q.unitary.round(2)
