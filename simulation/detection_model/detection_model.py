import itertools as it
import numpy as np
from collections import defaultdict

class detector:
    def __init__(self, label, efficiency, ratio, loss, mode):
        ''' a detector in place in the detection model '''
        self.label=label.upper()    # a helpful label
        self.efficiency=efficiency  # this detectors quantum efficiency
        self.ratio=ratio            # the ratio of light given to this detector by the preceeding splitter
        self.loss=loss              # the fibre loss prior to this splitter
        self.mode=mode              # the mode which this detector is attached to
        self.lumped_efficiency=self.efficiency*self.ratio*self.loss

    def __str__(self):
        ''' print out '''
        s='Detector %s (Efficiency %.2f, ' % (self.label, self.efficiency)
        s+='ratio %.2f, loss %.2f, ' % (self.ratio, 1-self.loss)
        s+='mode %d)' % self.mode
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
        self.detector_mode_map=[[] for i in range(16)]

    def provide_detector(self, name, efficiency):
        ''' provide a single detector '''
        self.all_detectors.append((name, efficiency))
        self.available_detectors.append((name, efficiency))

    def provide_detectors(self, names, efficiencies):
        ''' provide some detectors to use '''
        self.all_detectors=zip(names, efficiencies)
        self.available_detectors+=list(zip(names, efficiencies))
    
    def provide_splitter(self, label, ratio, loss):
        ''' provide a single splitter '''
        s=float(sum(ratio))
        ratio=tuple([x/s for x in ratio])
        n=len(ratio)
        self.all_splitters[n].append((label, ratio, loss))
        self.available_splitters[n].append((label, ratio, loss))

    def provide_splitters(self, label, ratios, losses):
        ''' provide some splitters to use '''
        for ratio, loss in zip(ratios, losses):
            self.provide_splitter(label, ratio, loss)
            
    def reset_shelf(self):
        ''' reset the list of available gear '''
        self.available_detectors=[x[:] for x in self.all_detectors]
        self.available_splitters=[x[:] for x in self.all_splitters]

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
        label, ratios, losses = splitter
        for ratio, loss in zip(ratios, losses):
            self.add_detector(mode, ratio, loss)
            
    def add_detector(self, mode, ratio=1, loss=1):
        ''' add a detector '''
        if len(self.available_detectors)==0: return
        label, detector_efficiency=self.available_detectors.pop(0)
        d=detector(label, detector_efficiency, ratio, loss, mode)
        self.detector_mode_map[mode].append(d)
        self.detectors.append(d)

    def get_detectors_from_mode(self, mode):
        ''' given a mode, return the detectors connected to that mode '''
        return self.detector_mode_map[mode]

    def get_mode_from_detector(self, label):
        ''' given a detector label, return the mode '''
        return self.detector_map[label.upper()].mode
    
    def iterate_over_mode_events(self, nphotons):
        ''' iterate over all unique "mode events" which can be detected using this detection scheme '''
        modes=[x.mode for x in self.detectors]
        return list(set(it.combinations(modes, nphotons)))

    def iterate_over_detector_events(self, nphotons):
        ''' iterate over all unique detection events which can be detected using this detection scheme '''
        return list(it.combinations(self.detectors, nphotons))
        
    def get_detector_event_efficiency(self, pattern):
        ''' get the lumped efficiency of a pattern of detectors '''
        return np.prod([det.lumped_efficiency for det in pattern])

    def get_efficiency_table(self, nphotons):
        ''' get efficiencies of all events that can be seen with this detection model '''
        table=defaultdict(int)
        for event in self.iterate_over_detector_events(nphotons):
            modes=tuple(sorted([d.mode for d in event]))
            table[modes]+=self.get_detector_event_efficiency(event)
        return table

    def show_available(self):
        ''' print all available gear '''
        s='Available detectors:\n'
        for detector in self.available_detectors:
            s+='%s (%.3f)\n' % detector
        s+='\nAvailable splitters:\n'
        for n, nfold in enumerate(self.available_splitters):
            if len(nfold)>0:
                s+='\n1-by-%d splitters:\n' % n
                for splitter in nfold:
                    label, ratios, losses = splitter
                    s+='%s: ' % label
                    s+= ', '.join(map(str, ratios))+'  |  '
                    s+= ', '.join(map(str, losses))+'\n'
        return s

    def draw(self):
        ''' draw the detection model '''
        s=''
        for mode in range(self.nmodes):
            s+= '\nMode: %d\n' % mode
            for detector in self.detector_mode_map[mode]:
                s+= '\-- %s\n' % (str(detector))
        return s

    def __str__(self):
        ''' printout '''
        return self.draw()


# Tests start here

if __name__=='__main__':
    # build a detection model
    m=detection_model(4)

    # provide some components
    m.provide_detectors('abcdefgh', [1]*8)
    m.provide_detector('z', 1)
    m.provide_splitter('tr0', (1,1,1),(1,1,1))
    for i in range(4):
        m.provide_splitter('sp_%d' % i, (1,1),(1,1))

    # show what we have available
    print m.show_available()

    # build the model with some splitters
    m.build('3210')
    print m.draw()

    # which detectors are connected to mode 2?
    print 'Detectors connected to mode 2:'
    for d in m.get_detectors_from_mode(2):
        print d

    print 'Detectors connected to mode 3:'
    for d in m.get_detectors_from_mode(0):
        print d

    # which mode is connected to detector F?
    print 'Mode', m.get_mode_from_detector('f'), 'is connected to F'
    
    # iterate over all the probabilitiy amplitudes that we would need to simulate 
    print '\nThree photon mode events which can be detected with this system:'
    for pattern in m.iterate_over_mode_events(3):
        print pattern

    # iterate over two-photon detection events that we might care about
    print '\nTwo-photon events'
    for pattern in m.iterate_over_detector_events(2):
        print ','.join([x.label for x in pattern])

    # iterate over all three-photon detection events, with efficiencies
    print '\nThree-photon events, with efficiencies'
    for pattern in m.iterate_over_detector_events(3):
        label = ','.join([x.label for x in pattern])
        label2= ','.join([str(x.mode) for x in pattern])

        efficiency = m.get_detector_event_efficiency(pattern)
        print '%s (%s): efficiency = %.3f' % (label, label2, efficiency)

    print '\nAll efficiencies, mapped to mode events'
    # iterate over all three-photon events, where we only care about modes, with efficiencies
    for event, efficiency in m.get_efficiency_table(3).items():
        print event, efficiency

