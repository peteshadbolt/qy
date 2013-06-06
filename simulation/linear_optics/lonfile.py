import numpy as np
from beamsplitter_network import beamsplitter_network

class lonfile(beamsplitter_network):
    ''' builds beamsplitter networks from a text file'''
    def __init__(self, filename):
        self.filename=filename
        self.structure=[]
        self.phaseshifters=[]
        self.beamsplitters=[]
        self.build()
        self.get_unitary()
        self.input_modes=[]

    def build(self):
        ''' build the structure '''
        f=open(self.filename, 'r')
        for line in f:
            b=line.split(' ')
            b=map(lambda x: x.lower().strip(), b)
            
            if b[0]=='name':
                self.name='%s (%s)' % (b[1], self.filename)

            if b[0]=='nmodes':
                self.nmodes=int(b[1])

            if b[0]=='bs':
                x=int(b[1]); y=int(b[2])
                splitting_ratio=float(b[3])
                self.add_beamsplitter(x,y,splitting_ratio)
                
            if b[0]=='ps':
                x=int(b[1]); y=int(b[2])
                self.add_phaseshifter(x,y)
