import itertools as it
import numpy as np
from scipy.misc import factorial

# useful function to invert efficiency matrices
invert_efficiency_matrix = np.vectorize(lambda a:  1/a if (a>0) else 0) 

class detector:
    def __init__(self, label, efficiency, ratio, loss, mode):
        self.label=label
        self.efficiency=efficiency
        self.ratio=ratio
        self.loss=loss
        self.mode=mode
        self.lumped_efficiency=self.efficiency*self.ratio*self.loss

    def __str__(self):
        ''' print out '''
        s='detector %s\n  quantum efficiency %.2f\n  ' % (self.label, self.efficiency)
        s+='ratio %.2f | loss %.2f\n' % (self.ratio, self.loss)
        s+='  connected to mode %d' % self.mode
        return s
        
class detection_model:
    def __init__(self, nmodes):
        ''' a model of some detection scheme '''
        self.nmodes=nmodes
        self.all_splitters=[[] for i in range(16)]
        self.available_splitters=[[] for i in range(16)]
        self.all_detectors=[]
        self.available_detectors=[]
        self.detectors=[]
        
    def net_efficiency(self, pattern):
        ''' get the lumped efficiency of a pattern of detectors '''
        return np.prod([det.lumped_efficiency for det in pattern])

    def provide_detector(self, name, efficiency):
        ''' provide a single detector '''
        self.all_detectors.append((name, efficiency))
        self.available_detectors.append((name, efficiency))

    def provide_detectors(self, names, efficiencies):
        ''' provide some detectors to use '''
        self.all_detectors=zip(names, efficiencies)
        self.available_detectors=zip(names, efficiencies)
        
    def map_pattern_to_modes(self, pattern):
        ''' map a list of detectors to a list of modes '''
        return map(lambda x: x.mode)
    
    def provide_splitter(self, ratio, loss):
        ''' provide a single splitter '''
        s=sum(ratio)
        ratio=tuple([x/s for x in ratio])
        self.all_splitters[len(ratio)].append([ratio, loss])
        self.available_splitters[len(ratio)].append([ratio, loss])

    def provide_splitters(self, ratios, losses):
        ''' provide some splitters to use '''
        for ratio, loss in zip(ratios, losses):
            self.provide_splitter(ratio, loss)
            
    def reset_shelf(self):
        ''' reset the list of available gear '''
        self.available_detectors=[x[:] for x in self.all_detectors]
        self.available_splitters=[x[:] for x in self.all_splitters]
        
    def detector_pattern(self, pattern):
        ''' look up a set of detectors '''
        return [self.detector_map[x] for x in sorted(pattern.lower())]

    def get_modes(self, pattern):
        ''' get a sorted tuple of modes corresponding to a given detection pattern '''
        return tuple(sorted([d.mode for d in self.detector_pattern(pattern)]))

    def build(self, scheme_string):
        ''' build the whole thing '''
        self.reset_shelf()
        self.detectors=[]
        self.used_modes=set()
        # while you haven't run out of detectors...
        mode=0
        while len(self.available_detectors)>0 \
               and len(self.available_splitters)>0 \
               and mode<self.nmodes:
            ndetectors=int(scheme_string[mode % len(scheme_string)])
            if ndetectors>0: self.used_modes.add(mode)
            if ndetectors==1: self.add_detector(mode)
            if ndetectors>1: self.add_splitter(ndetectors, mode)
            mode+=1
        self.detector_map={d.label:d for d in self.detectors}
                        
    def add_splitter(self, ndetectors, mode):
        ''' add a mode '''
        if len(self.available_splitters[ndetectors])==0: return
        splitter=self.available_splitters[ndetectors].pop(0)
        for arm in zip(*splitter):
            ratio, loss=arm
            if len(self.available_detectors)==0: return
            label, detector_efficiency=self.available_detectors.pop(0)
            d=detector(label, detector_efficiency, ratio, loss, mode)
            self.detectors.append(d)
            
    def add_detector(self, mode):
        ''' add a detector '''
        ratio, loss=1,1
        if len(self.available_detectors)==0: return
        label, detector_efficiency=self.available_detectors.pop(0)
        d=detector(label, detector_efficiency, ratio, loss, mode)
        self.detectors.append(d)

    def show_available(self):
        ''' print all available gear '''
        s='AVAILABLE DETECTORS:\n'
        for detector in self.available_detectors:
            s+='%s (%.3f)\n' % detector
        s='\nAVAILABLE SPLITTERS:\n'
        for splitter in self.available_splitters:
            s+='%s (%.3f)\n' % detector

    def __str__(self):
        ''' printout '''
        s='DETECTION SCHEME:\n'
        return s+'\n\n'.join(map(str, self.detectors))

    def get_used_modes(self):
        ''' just return the modes that are connected to something '''
        return list(self.used_modes)

    def get_mode_events(self, nphotons):
        ''' list the different unique combinations of modes which can be addressed using this scheme, given some photon number '''
        return 'awd'

    def get_detector_events(self, nphotons):
        ''' list all the ways that the used detectors can click '''
        detector_indeces=range(len(self.detectors))
        indeces=it.combinations(detector_indeces, nphotons)
        detectors=[[self.detectors[i] for i in pattern] for pattern in indeces]
        return detectors

    def get_detector_label_events(self, nphotons):
        ''' list all the ways that the used detectors can click '''
        detector_indeces=range(len(self.detectors))
        indeces=it.combinations(detector_indeces, nphotons)
        detectors=[''.join(sorted([self.detectors[i].label for i in pattern])) for pattern in indeces]
        return detectors
    
    def patterns_and_efficiencies(self, nphotons):
        ''' iterate over all patterns of n photons, with efficiencies '''
        indeces=it.combinations(range(len(self.detectors)), nphotons)
        detectors=[[self.detectors[i] for i in pattern] for pattern in indeces]
        efficiencies=map(lambda x: self.net_efficiency(x), detectors)
        return zip(detectors, efficiencies)
                


#def patterns_and_efficiencies(self, nphotons):
        #''' iterate over all patterns of n photons, with efficiencies '''
        #combinations=list(it.permutations(self.detectors, nphotons))
        #efficiencies=map(lambda x: self.net_efficiency(x), combinations)
        #return zip(combinations, efficiencies)

    #def choose_n_photons(self, nphotons):
        #''' iterate over all combinations of detectors '''
        #return it.permutations(self.detectors, nphotons)

    #def efficiency_matrix(self, nphotons):
        #''' generate a sparse efficiency matrix for n photons '''
        #sparse={}
        #for pattern in self.choose_n_photons(nphotons):
            #net_efficiency=self.net_efficiency(pattern)
            #position=tuple(sorted([det.mode for det in pattern]))
            #if position in sparse: 
                #sparse[position]+=net_efficiency
            #else:
                #sparse[position]=net_efficiency
        #return sparse
    
