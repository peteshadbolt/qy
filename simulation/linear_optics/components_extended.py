import numpy as np

class crossing:
    def __init__(self,x,y,index):
        self.x=x
        self.y=y
        self.index=index
        
    def get_unitary(self):
        return np.matrix([[0,1],[1,0]])
        
    def draw(self, axis, text=True):
        ''' draw the crossing '''
        shape1x=np.array([0, 0.2, 0.8, 1])
        shape1y=np.array([0, 0, 1, 1])
        shape2x=np.array([0, 0.2, 0.4, 0.4, 0.6, 0.8, 1])
        shape2y=np.array([1, 1, 0.666, 0.333, 0.333, 0, 0])
        t=.2
        axis.plot(shape1x+self.x, shape1y+self.y, 'k-')
        axis.plot(shape2x+self.x, shape2y+self.y, 'k-')
        if text:
            color='#880000'
            axis.text(self.x+.5, self.y+.2, 'C%d' % self.index, color=color, fontsize=5, ha='center', va='bottom')
        
    def __str__(self):
        return 'crossing %d [%d,%d]' % (self.index, self.x, self.y)

        

class beamsplitter:
    def __init__(self, x, y, index, ratio=.5):
        ''' a splitter '''
        self.x=x
        self.y=y
        self.index=index
        self.set_splitting_ratio(ratio)
        
    def set_splitting_ratio(self, splitting_ratio):
        ''' change my degree of freedom '''
        self.splitting_ratio=splitting_ratio % 1
        
    def get_unitary(self):
        ''' get my unitary '''
	return np.matrix([[np.sqrt(self.splitting_ratio), 1j*np.sqrt(1-self.splitting_ratio)],[1j*np.sqrt(1-self.splitting_ratio), np.sqrt(self.splitting_ratio)]], dtype=complex)
        #return np.matrix([[1,1],[1,-1]])/np.sqrt(2)
        
    def draw(self, axis, text=True):
        ''' draw the splitter '''
        shape1x=np.array([0, 0.2, 0.8, 1])
        shape1y=np.array([0, 0, 1, 1])
        shape2x=np.array([0, 0.2, 0.8, 1])
        shape2y=np.array([1, 1, 0, 0])
        t=.2
        shape3x=np.array([0.5-t, 0.5+t])
        shape3y=np.array([.5,.5])
        axis.plot(shape1x+self.x, shape1y+self.y, 'k-')
        axis.plot(shape2x+self.x, shape2y+self.y, 'k-')
        axis.plot(shape3x+self.x, shape3y+self.y, 'k-', alpha=self.splitting_ratio)
        if text:
            color='#880000'
            axis.text(self.x+.5, self.y+.2, 'S%d' % self.index, color=color, fontsize=5, ha='center', va='bottom')
            axis.text(self.x+.8, self.y+.5, 'r=%.1f' % self.splitting_ratio, color=color, fontsize=5, ha='left', va='center')
        
    def __str__(self):
        ''' print '''
        return 'splitter %d [%d,%d]      \t| splitting_ratio =%.2f' % (self.index, self.x, self.y, self.splitting_ratio)

class phaseshifter:
    def __init__(self, x, y, index, phase=0, invert=False):
        ''' a splitter '''
        self.x=x
        self.y=y
        self.index=index
        self.invert=invert
        self.set_phi(phase)
        
    def set_phi(self, phi):
        ''' change my degree of freedom '''
        self.phi=phi % (2*np.pi)
        
    def get_unitary(self):
        ''' get my unitary '''
        if self.invert:
            return np.matrix([[np.exp(1j*self.phi),0],[0,1]], dtype=complex)
        else:
            return np.matrix([[1,0],[0,np.exp(1j*self.phi)]], dtype=complex)
        
    def draw(self, axis, text=True):
        ''' draw the splitter '''
        l=.1
        xo=np.sin(self.phi)*.1
        yo=np.cos(self.phi)*.1
        x,y = (self.x, self.y) if self.invert else (self.x, self.y+1)
        axis.plot([x+.5], [y], 'k.', zorder=150)
        p=axis.plot([x+.5, x+.5+xo], [y, y-yo], lw=1, color='red', zorder=100)
        
        if text:
            axis.text(self.x+.5, self.y+.8, 'P%d' % self.index, color='#4444ff', fontsize=5, ha='center', va='center')
        
    def __str__(self):
        ''' print '''
        return 'phase shifter %d [%d,%d] \t| phase =%.2f pi' % (self.index, self.x, self.y, self.phi/np.pi)
        
class phaseshifter_extended:
    def __init__(self, x, y,a,b,index, v=0, phase=0, invert=False):
        ''' a splitter '''
        self.x=x
        self.y=y
        #these are the phase-voltage parameters (phi=a+b*v^2)
        self.a=a
        self.b=b
        self.index=index
        self.invert=invert
        self.set_phi(phase)
        self.set_v(v)
        
    def set_phi(self, phi):
        ''' change my degree of freedom '''
        self.phi=phi % (2*np.pi)
        
    def set_v(self,v):
        self.v=v
        phi=self.a+self.b*(v**2)
        self.set_phi(phi)
        
    def set_phase_offset(self,offset):
        self.a=offset
        
    def set_phase_quadratic_term(self,quad):
        self.b=quad
        
    def get_unitary(self):
        ''' get my unitary '''
        if self.invert:
            return np.matrix([[np.exp(1j*self.phi),0],[0,1]], dtype=complex)
        else:
            return np.matrix([[1,0],[0,np.exp(1j*self.phi)]], dtype=complex)
        
    def draw(self, axis, text=True):
        ''' draw the splitter '''
        l=.1
        xo=np.sin(self.phi)*.1
        yo=np.cos(self.phi)*.1
        x,y = (self.x, self.y) if self.invert else (self.x, self.y+1)
        axis.plot([x+.5], [y], 'k.', zorder=150)
        p=axis.plot([x+.5, x+.5+xo], [y, y-yo], lw=1, color='red', zorder=100)
        
        if text:
            axis.text(self.x+.5, self.y+.8, 'P%d' % self.index, color='#4444ff', fontsize=5, ha='center', va='center')
        
    def __str__(self):
        ''' print '''
        return 'phase shifter (extended) %d [%d,%d] \t| phase =%.2f pi' % (self.index, self.x, self.y, self.phi/np.pi)

class static_phase:
    def __init__(self,x,y,phase,index,invert=False):
        self.x=x
        self.y=y
        self.phi=phase%(2*np.pi)
        self.invert=invert
        self.index=index
        
    def set_offset(self,offset):
        self.phi=offset%(2*np.pi)

    def get_unitary(self):
        ''' get my unitary '''
        if self.invert:
            return np.matrix([[np.exp(1j*self.phi),0],[0,1]], dtype=complex)
        else:
            return np.matrix([[1,0],[0,np.exp(1j*self.phi)]], dtype=complex)

    def draw(self, axis, text=True):
        ''' draw the splitter '''
        l=.1
        xo=np.sin(self.phi)*.1
        yo=np.cos(self.phi)*.1
        x,y = (self.x, self.y) if self.invert else (self.x, self.y+1)
        axis.plot([x+.5], [y], 'k.', zorder=150)
        p=axis.plot([x+.5, x+.5+xo], [y, y-yo], lw=1, color='red', zorder=100)
        
        if text:
            axis.text(self.x+.5, self.y+.8, 'P%d' % self.index, color='#4444ff', fontsize=5, ha='center', va='center')
    
    def __str__(self):
        ''' print '''
        return 'static phase %d [%d,%d] \t| phase =%.2f pi' % (self.index, self.x, self.y, self.phi/np.pi)