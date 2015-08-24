import numpy as np
from beamsplitter_phase_network import beamsplitter_phase_network
import json

class reck_scheme(beamsplitter_phase_network):
    ''' builds beamsplitter networks according to reck et al'''
    def __init__(self, nmodes, dense_phase_shifters=False):
        ''' dense phase shifters gives us more PS than we strictly need '''
        self.name='reck scheme'
        self.nmodes=nmodes
        self.dense_phase_shifters=dense_phase_shifters
        self.structure=[]
        self.phaseshifters=[]
        self.phaseshifters_extended=[]
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
            self.add_phaseshifter_extended(x,modenum)
            
    def buildend(self):
        n = self.nmodes
        x = 4 + 8*(n-2)
        for y in range(n-1):
            self.add_phaseshifter(x,y)
            
        
            
    def build(self):
        for modenum in range(self.nmodes-1):
            self.buildrow(modenum)
        #self.buildend()
        self.order_structure()
        
        #this doesn't work. need to order by x values
        
    def set_random_phases(self):
        p = np.random.uniform(0,2*np.pi,len(self.phaseshifters))
        self.set_phases(p)
        
    def order_structure(self):
        self.structure = sorted(self.structure, key=lambda s: s.x)
        
    def set_realistic_shifter_parameters(self):
        for p in self.phaseshifters_extended:
            p.set_phase_offset(np.random.uniform(0,np.pi/2.))
            p.set_phase_offset(np.random.normal(0.14,0.01))
            
    def set_realistic_splitting_ratios(self):
        for s in self.beamsplitters:
            s.set_splitting_ratio(np.random.normal(0.5,0.01))
            
    def to_dict(self):
        couplers=[]
        for c in self.beamsplitters:  
            couplers.append({'y':c.y, 'x':c.x, 'ratio':c.splitting_ratio})
        shifters=[]
        for s in self.phaseshifters_extended:
            shifters.append({'y':s.y, 'x':s.x, 'phase':s.phi, 'pva':s.a, 'pvb':s.b})
        d={}
        d['name']='reck_scheme'
        d['modes']=self.nmodes
        d['width']=(np.max([c.x for c in self.structure])+2)
        d['couplers']=couplers
        d['extended_shifters']=shifters
        
        self.asdict=d
            
    def to_json(self,filename='test.json'):
        self.to_dict()
        f=open(filename,'w')
        json.dump(self.asdict,f, indent=4)
        
        
        
        
if __name__ == "__main__":
    r=reck_scheme(6)
    r.set_realistic_splitting_ratios()
    print r
    r.to_json()