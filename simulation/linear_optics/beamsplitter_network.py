from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import rc 

import numpy as np
import json
import components

class beamsplitter_network:
    '''an object which describes a beamsplitter network'''
    def __init__(self, nmodes=None, json=None):
        self.nmodes = nmodes
        self.name='beamsplitter network'
        self.structure=[]
        self.phaseshifters=[]
        self.crossings=[]
        self.beamsplitters=[]
        self.input_modes=[]
        self.unitary=None
        if json!=None: self.from_json(json)

    def from_json(self, json_filename):
        ''' build the structure '''
        f=open(json_filename); s=f.read(); f.close();
        jsondata=json.loads(s)
        self.nmodes=jsondata['modes']
        self.name=jsondata['name']
        self.width=jsondata['width']
        things=jsondata['couplers']+jsondata['shifters']
        things=sorted(things, key=lambda thing: thing['x'])
        for thing in things:
            if 'phase' in thing:
                self.add_phaseshifter(thing['x'], thing['y'])
            elif 'ratio' in thing:
                self.add_beamsplitter(thing['x'], thing['y'], thing['ratio'])
        self.get_unitary()

    def get_ndof(self):
        '''get the number of degrees of freedom'''
        return len(self.phaseshifters)+len(self.beamsplitters)

    def set_input_modes(self, mode_list):
        ''' set the input modes '''
        self.input_modes=mode_list

    def add_beamsplitter(self, x, y, splitting_ratio=.5):
        '''add a beamsplitter at position (x,y)'''
        bs=components.beamsplitter(x,y, len(self.beamsplitters), splitting_ratio)
        self.structure.append(bs)
        self.beamsplitters.append(bs)
        
    def add_crossing(self,x,y):
        cross=components.crossing(x,y,len(self.crossings))
        self.structure.append(cross)
        self.crossings.append(cross)

    def add_phaseshifter(self, x, y, phase=0, invert=False):
        '''add a beamsplitter at position (x,y)'''
        ps=components.phaseshifter(x,y, len(self.phaseshifters), phase, invert)
        self.structure.append(ps)
        self.phaseshifters.append(ps)
        
    def set_phases(self, new_phases):
        ''' set the phases '''
        for shifter, phase in zip(self.phaseshifters, new_phases):  
            shifter.set_phi(phase)
        self.get_unitary()
   
    def set_splitting_ratios(self, new_splitting_ratios):
        ''' set the phases '''
        for splitter, splitting_ratio in zip(self.beamsplitters, new_splitting_ratios): 
            splitter.set_splitting_ratio(splitting_ratio)
        self.get_unitary()

    def set_parameters(self, p):
        ''' set all parameters'''
        nps=len(self.phaseshifters)
        self.set_phases(p[:nps])
        self.set_splitting_ratios(p[nps:])
        self.get_unitary()

    def get_unitary(self):
        ''' build the unitary '''
        #TODO: this can be optimized by generating columns	
        self.unitary=np.matrix(np.eye(self.nmodes), dtype=complex)
        for o in reversed(self.structure):
            u=np.matrix(np.eye(self.nmodes, dtype=complex))
            u[o.y:o.y+2, o.y:o.y+2]=o.get_unitary()
            self.unitary*=u
        return self.unitary
    
    def __str__(self):
        ''' make a string representing the beamsplitter network '''
        s='%d-mode %s\n' % (self.nmodes, self.name)
        s+='%d phase shifters | ' % len(self.phaseshifters)
        s+='%d beam splitters | ' % len(self.beamsplitters)
        s+='%d degrees of freedom\n' % (len(self.phaseshifters)+len(self.beamsplitters))

        for i, component in enumerate(self.structure):
            s+='  (#%d) %s\n' % (i, str(component))
        return s

    def draw(self, filename='figures/out.pdf'):
        ''' draw the thing '''
        #print 'drawing beamsplitter network...',
        if len(self.structure)==0:
            max_x=1
        else:
            max_x=max([q.x for q in self.structure])

        # build a figure and some axes
        self.figure=Figure(figsize=(10*(max_x+2)/10.,5*self.nmodes/10.))
        self.canvas=FigureCanvas(self.figure)
        self.axes=self.figure.add_subplot(111)
        self.axes.axis('off')       

        # draw and label the modes
        for i in range(self.nmodes):
            self.axes.plot([-1, max_x+2], [i,i], '-', color='#cccccc')
            self.axes.text(-1.2, i, '%d' % i, va='center', fontsize=8, ha='center')
            self.axes.text(max_x+4-1.8, i, '%d' % i, va='center', fontsize=8, ha='center')
            #if i in self.inputs: self.axes.plot([-1.5], [i], 'ro')

        # draw the input photons
        for offset, group in enumerate(self.input_modes):
            x=-1.9+offset*.1
            self.axes.plot([x, x], [0, self.nmodes-1], '-', color='#ffcccc')
            old_g=None
            for g in group:
                if g==old_g: 
                    x+=.05
                else:
                    x=-1.9+offset*.1
                self.axes.plot(x, g, 'r.')
                old_g=g
        
        # draw all the beamsplitters and phase shifters
        for object in self.structure:
            object.draw(axis=self.axes, text=self.nmodes<20)
                
        self.axes.set_ylim((self.nmodes-.5),-1)
        self.axes.set_xlim(-2, max_x+3)
        self.axes.set_aspect(.5)
        self.canvas.print_figure(filename, bbox_inches='tight')
        #print 'done'
