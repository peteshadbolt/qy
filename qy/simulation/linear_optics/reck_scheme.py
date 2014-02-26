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
        self.get_unitary()

    def build_column(self, x, height):
        ''' build a column '''
        splitter_y=lambda x: range(x%2,x+1,2)
        if self.dense_phase_shifters:
            phase_y=lambda x: range(x%2,x+1,2)
        else:
            phase_y=lambda x: range(0,x+1,2) if x%2==0 else []

        for y in phase_y(height):
            self.add_phaseshifter(x,self.nmodes-2-y, invert=True)
        for y in splitter_y(height):
            self.add_beamsplitter(x,self.nmodes-2-y)

    def build(self):
        ''' build the structure '''
        #if self.dense_phase_shifters: self.ps_column()
        # first triangle
        for x in range(self.nmodes-1):
            self.build_column(x, x)
        # second triangle
        for x in range(self.nmodes-1, self.nmodes*2-1):
            height=self.nmodes*2-4-x
            self.build_column(x, height)
