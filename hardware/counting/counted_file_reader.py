import counted_file_parser
import qy
import numpy as np
import os

class curve:
	def __init__(self, label, pattern, nsteps, nloops, filename):
		self.label=label
		self.pattern=pattern
		self.nsteps=nsteps
		self.nloops=nloops
		self.filename=filename
		self.rates=np.zeros((nsteps, nloops))
				
	def add_rate(self, step, loop, rate):
		''' add a new count rate '''
		try:
			self.rates[step, loop]=rate
		except IndexError:
			print 'index error reading file %s, ignored' % self.filename
			return
			
	def trim(self, max_step, max_loop):
		self.nsteps=max_step
		self.nloops=max_loop
		self.rates=self.rates[:max_step, :max_loop]

class position_handler:
	def __init__(self, nsteps, nloops, filename, motor_index):
		self.motor_index=motor_index
		self.nsteps=nsteps
		self.nloops=nloops
		self.filename=filename
		self.positions=np.zeros((nsteps, nloops))
				
	def add_position(self, step, loop, rate):
		''' add a new count rate '''
		try:
			self.positions[step, loop]=rate		
		except IndexError:
			print 'index error reading file %s, ignored' % self.filename
			return
			
	def trim(self, max_step, max_loop):
		self.nsteps=max_step
		self.nloops=max_loop
		self.positions=self.positions[:max_step, :max_loop]
		
class counted_file_reader:
	def __init__(self, fname):
		self.patterns=[]
		self.filename=fname
		self.file_open=False
		self.filesize=0
		self.max_loop=0
		self.max_step=0
		self.all_triplets=0
		self.progress=0
		self.error=0
		self.get_metadata()
		self.set_patterns('')
		
	def get_metadata(self):
		''' read all the metadata '''
		self.filesize=os.path.getsize(self.filename)
		counted_file_parser.open_counted_file(self.filename)
		counted_file_parser.read_metadata()
		
		self.scan_label=counted_file_parser.get_scan_label()
		self.scan_nloops=counted_file_parser.get_scan_nloops()
		self.scan_nsteps=counted_file_parser.get_scan_nsteps()
		self.scan_integration_time=counted_file_parser.get_scan_integration_time()
		self.scan_close_shutter=counted_file_parser.get_scan_close_shutter()
		
		self.scan_type=counted_file_parser.get_scan_type()
		self.scan_dont_move=counted_file_parser.get_scan_dont_move()
		
		self.scan_motor_controller=counted_file_parser.get_scan_motor_controller()
		self.scan_start_postion=counted_file_parser.get_scan_start_position()
		self.scan_stop_position=counted_file_parser.get_scan_stop_position()
		
		counted_file_parser.close_counted_file()
		self.file_open=False
		
	def get_curves(self):
		''' get the curves, integrated or not integrated '''
		return [c.rates for c in self.curves]
	
	def get_description(self):
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
		
	def set_patterns(self, pattern_labels):
		''' set the patterns '''
		self.patterns=qy.hardware.counting.parser.parse_pattern_list(pattern_labels, False)
		q=zip(self.patterns, pattern_labels)
		q=filter(lambda x: x[0]!=None, q)
		self.patterns, pattern_labels=zip(*q) if q!=[] else ([],[])
		self.pattern_labels=pattern_labels
		
		# zero the positions
		self.positions=[]
		for i in range(qy.settings.get('motors.count')):
			pos=position_handler(self.scan_nsteps, self.scan_nloops, self.filename, i)
			self.positions.append(pos)

		# zero the curves
		self.curves=[]
		for i in range(len(pattern_labels)):
			c=curve(self.pattern_labels[i], self.patterns[i], self.scan_nsteps, self.scan_nloops, self.filename)
			self.curves.append(c)
		
	def read_chunk(self):
		''' read a chunk of data '''
		if not self.file_open: 
			counted_file_parser.open_counted_file(self.filename)
			counted_file_parser.read_metadata()
			self.file_open=True
			
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
		
		# append all the rates to the curves
		for curve in self.curves:
			rate=0
			pattern=curve.pattern
			if pattern[1]==1: 
				rate=counted_file_parser.get_fpga_rate(pattern[0])
			elif pattern[1]==2: 
				if len(pattern[0])==2: rate=counted_file_parser.get_number_rate_8x2(*pattern[0])
				if len(pattern[0])==4: rate=counted_file_parser.get_number_rate_4x4(*pattern[0])
			elif pattern[1]==3: 
				rate=counted_file_parser.get_special_rate(len(pattern[0]))
			curve.add_rate(step, loop, rate)
			
		# and the position handler
		for i in range(qy.settings.get('motors.count')):
			position=counted_file_parser.get_motor_controller_position(i)
			self.positions[i].add_position(step, loop, position)
		return triplet_count
		
	def trim(self, max_step=None, max_loop=None):
		''' trim count rates etc to throw out unused loops / steps '''
		if max_step==None: max_step=self.max_step
		if max_loop==None: max_loop=self.max_loop
		
		for curve in self.curves:
			curve.trim(max_step, max_loop)
		for position in self.positions:
			position.trim(max_step, max_loop)
			
			
