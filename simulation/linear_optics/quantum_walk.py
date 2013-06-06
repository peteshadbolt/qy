import numpy as np
import scipy as sp
import scipy.linalg
from perm import perm_ryser
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

class quantum_walk:
    '''an object which describes a quantum_walk'''
    def __init__(self, nmodes=21, coupling=0.5, beta=1.0, time=1):
        self.nmodes = nmodes
        self.name='quantum_walk'
        self.hamiltonian=np.matrix(np.zeros([self.nmodes, self.nmodes]))
        self.set_time(time)
        self.set_diagonal(beta)
        self.set_off_diagonal(coupling)
        self.get_unitary()
        self.input_modes=[]

    def set_input_modes(self, mode_list):
        ''' set the input modes '''
        self.input_modes=mode_list

    def set_diagonal(self, beta):
        ''' calculate the hamiltonian ''' 
        self.onsite_potential=np.ones(self.nmodes)*beta
        self.average_onsite_potential=np.average(self.onsite_potential)
        for i in range(self.nmodes):
            self.hamiltonian[i,i]=self.onsite_potential[i]
        self.get_unitary()

    def set_off_diagonal(self, coupling):
        self.coupling=np.ones(self.nmodes-1)*coupling
        self.average_coupling=np.average(self.coupling)
        for i in range(self.nmodes-1):
            self.hamiltonian[i, i+1]=self.coupling[i]
            self.hamiltonian[i+1, i]=self.coupling[i]
        self.get_unitary()

    def set_time(self, time):
        ''' set the time parameter '''
        self.time=time
        self.get_unitary()

    def get_unitary(self):
        ''' build the unitary '''
        self.unitary=np.matrix(sp.linalg.expm(-1j*self.hamiltonian*self.time))
        return self.unitary
    
    def __str__(self):
        ''' make a string representing the quantum walk'''
        s='%d-mode %s\n' % (self.nmodes, self.name)
        p=(self.average_coupling, self.average_onsite_potential)
        s+='average coupling: %.2f \t|\taverage on-site potential %.2f' % p
        return s

    def draw(self, filename='figures/out.pdf'):
        ''' draw the quantum walk'''
        print 'drawing quantum walk...',
        max_x=1

        # build a figure and some axes
        self.figure=Figure(figsize=(10*(max_x+2)/7.,5*self.nmodes/7.))
        self.canvas=FigureCanvas(self.figure)
        self.axes=self.figure.add_subplot(111)
        self.axes.axis('off')       

        # draw and label the modes
        y=0
        for i in range(self.nmodes):
            self.axes.plot([-1, max_x+2], [y,y], '-', color='#000000', lw=1*self.onsite_potential[i])
            self.axes.text(-1.5, y, '%d' % i, va='center', fontsize=8, ha='center')
            self.axes.text(max_x+4-1.5, y, '%d' % i, va='center', fontsize=8, ha='center')
            y+=np.abs(self.coupling[i%(self.nmodes-1)]*2)
        
        self.axes.set_ylim(-1, y+1)
        self.axes.set_xlim(-2, max_x+3)
        self.axes.set_aspect(.5)
        self.canvas.print_figure(filename, bbox_inches='tight')
        print 'done'
