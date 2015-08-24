import numpy as np
from beamsplitter_network import beamsplitter_network

class reck_scheme(beamsplitter_network):
    ''' builds beamsplitter networks according to reck et al'''
    def __init__(self, nmodes, dense_phase_shifters=False):
        ''' dense phase shifters gives us more PS than we strictly need '''
        self.name='reck scheme'
        self.nmodes=nmodes
        self.dense_phase_shifters=dense_phase_shifters
        self.structure=[]
        self.phaseshifters=[]
        self.beamsplitters=[]
        self.input_modes=[]
        self.build()
        self.unitary = self.get_unitary()

    def buildrow(self, modenum):
        #The total number of 'blocks' in the row is equal to the mode number (mode number starts from 0 at the top)
        #4 elements in each block
        xboost = (self.nmodes-2-modenum)*4
        bs_x_vals = np.hstack([np.array([1,3])+a+xboost for a in np.array(range(modenum+1))*8])
        ps_x_vals = np.hstack([np.array([0,2])+a+xboost for a in np.array(range(modenum+1))*8])
        #add the beamsplitters
        for x in bs_x_vals:
            self.add_beamsplitter(x,modenum)
        
        #add the phaseshifters
        for x in ps_x_vals:
            self.add_phaseshifter(x,modenum)
            
    def buildend(self):
        n = self.nmodes
        x = 4 + 8*(n-2)
        for y in range(n-1):
            self.add_phaseshifter(x,y)
            
        
            
    def build(self):
        for modenum in range(self.nmodes-1):
            self.buildrow(modenum)
        self.buildend()
        self.order_structure()
        
        #this doesn't work. need to order by x values
        
    def set_random_phases(self):
        p = np.random.uniform(0,2*np.pi,len(self.phaseshifters))
        self.set_phases(p)
        
    def order_structure(self):
        self.structure = sorted(self.structure, key=lambda s: s.x)
        