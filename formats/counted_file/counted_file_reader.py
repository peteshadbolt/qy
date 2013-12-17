import _counted_file_parser as counted_file_parser
import numpy as np
import os
import parser
from qy import util

class counted_file_reader:
    def __init__(self, fname, patterns=None, silent=False):
        self.filename=fname
        self.filesize=0
        self.max_loop=0
        self.max_step=0
        self.all_triplets=0
        self.progress=0
        self.error=0
        self.silent=silent
        self.load_metadata()
        if patterns!=None: self.load(patterns)

    def load_metadata(self):
        ''' read all the metadata '''
        self.filesize=os.path.getsize(self.filename)
        self.total_chunks=self.filesize/(4*3)
        counted_file_parser.open_counted_file(self.filename)
        counted_file_parser.read_metadata()
        self.scan_motors_count=3
        self.scan_label=counted_file_parser.get_scan_label()[:-1]
        self.scan_nloops=counted_file_parser.get_scan_nloops()
        self.scan_nsteps=counted_file_parser.get_scan_nsteps()
        self.scan_integration_time=counted_file_parser.get_scan_integration_time()
        self.scan_close_shutter=counted_file_parser.get_scan_close_shutter()
        self.scan_type=counted_file_parser.get_scan_type()
        self.scan_dont_move=counted_file_parser.get_scan_dont_move()
        self.scan_motor_controller=counted_file_parser.get_scan_motor_controller()
        self.scan_start_postion=counted_file_parser.get_scan_start_position()
        self.scan_stop_position=counted_file_parser.get_scan_stop_position()
        
    def load(self, patterns, callback=None, trim=True):
        ''' load all data in the file without a callback or anything '''
        self.set_patterns(patterns)
        loading_messsage='loading %s (%d kB)...' % (os.path.split(self.filename)[-1], self.filesize/1024.)
        chunks_read=1
        total=0
        while chunks_read>0:
            chunks_read=self.read_chunk() 
            if callback!=None: callback(total)
            util.progress_bar(self.progress*100, 100, loading_messsage)
            total+=1
        if trim: self.trim()
        if not self.silent: print
        return total

    def set_patterns(self, pattern_labels):
        ''' set the patterns '''
        patterns=parser.parse_pattern_list(pattern_labels, False)
        self.patterns=[p for p in patterns if p!=None]
        self.pattern_labels=[pattern_labels[i] for i in range(len(patterns)) if patterns[i]!=None]
        self.positions=np.zeros((self.scan_motors_count, self.scan_nsteps, self.scan_nloops))
        self.counts=np.zeros((len(self.patterns), self.scan_nsteps, self.scan_nloops))

    def get_count_rate(self, pattern):
        ''' get a count rate given a pattern '''
        if pattern[1]==1: 
            return counted_file_parser.get_fpga_rate(pattern[0])
        elif pattern[1]==2: 
            if len(pattern[0])==2: return counted_file_parser.get_number_rate_8x2(*pattern[0])
            if len(pattern[0])==4: return counted_file_parser.get_number_rate_4x4(*pattern[0])
        elif pattern[1]==3: 
            return counted_file_parser.get_special_rate(len(pattern[0]))
        return 0
        
    def read_chunk(self):
        ''' read a chunk of data '''
        # read the chunk
        triplet_count=counted_file_parser.read_chunk()

        # if this chunk was aborted, return nothing
        if counted_file_parser.get_aborted(): return 0
        
        # get the step and loop
        step=counted_file_parser.get_scan_step()
        loop=counted_file_parser.get_scan_loop()
        self.max_step=max(step+1, self.max_step)
        self.max_loop=max(loop+1, self.max_loop)
        self.all_triplets+=triplet_count
        self.progress=self.all_triplets*3*4/float(self.filesize)
        
        # write down the count rates
        for pattern_index, pattern in enumerate(self.patterns):
            self.counts[pattern_index, step, loop]=self.get_count_rate(pattern)
            
        # write down the positions
        for motor_index in range(self.scan_motors_count):
            position=counted_file_parser.get_motor_controller_position(motor_index)
            self.positions[motor_index, step, loop]=position
        return triplet_count
        
    def trim(self):
        ''' trim count rates etc to throw out unused loops / steps '''
        self.counts=self.counts[:, 0:self.max_step, 0:self.max_loop]
        self.positions=self.positions[:, 0:self.max_step, 0:self.max_loop]

    def counts_positions_labels(self):
        ''' helper function '''
        return self.counts, self.positions, self.pattern_labels
            
    def __str__(self):
        ''' get a long string summarizing the metadata '''
        s='Filename: '+self.filename+'\n'
        s+='Label: '+' '.join(self.scan_label.split('\n'))+'\n'
                
        # scan type
        if self.scan_type==101: s+='Scan mode: Dip/fringe\n'
        if self.scan_type==102: s+='Scan mode: Static sample\n'
        if self.scan_type==103: s+='Scan mode: Multiposition sample\n'
        
        # more metadata
        s+='%d loops, %d steps per loop. ' % (self.scan_nloops, self.scan_nsteps)+'\n'
        s+='Integration time: %ds. ' % (self.scan_integration_time)+'\n'
        if self.scan_close_shutter: s+='Tried to close the shutter at end of scan.\n'
        
        # movement state
        if self.scan_dont_move==1: s+='Motor controllers were all stationary\n'
        if self.scan_dont_move==0: s+='Moved MC%d from %.5fmm to %.5fmm\n' % (self.scan_motor_controller+1, self.scan_start_postion, self.scan_stop_position)
        if self.scan_type==101: s+='Moved MC%d from %.5fmm to %.5fmm\n' % (self.scan_motor_controller+1, self.scan_start_postion, self.scan_stop_position)
        return s
