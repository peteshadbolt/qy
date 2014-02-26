import counted_file_parser
import qy
import numpy as np

class curve:
	def __init__(self, label, pattern, npoints, nloops):
		self.label=label
		self.pattern=pattern
		self.npoints=npoints
		self.nloops=nloops
		self.positions=np.zeros((npoints, nloops))
		self.rates=np.zeros((npoints, nloops))
		
	def add_rate(self, point, loop, position, rate):
		''' add a new count rate '''
		self.positions[point, loop]=position
		self.rates[point, loop]=rate

class counted_file_reader:
	def __init__(self, fname):
		self.patterns=[]
		self.filename=fname
		self.file_open=False
		self.get_metadata()
		self.set_patterns('')
		
	def get_metadata(self):
		''' read all the metadata '''
		counted_file_parser.open_counted_file(self.filename)
		counted_file_parser.read_metadata()

		self.scan_label=counted_file_parser.get_scan_label()
		self.scan_nloops=counted_file_parser.get_scan_nloops()
		self.scan_npoints=counted_file_parser.get_scan_npoints()
		self.scan_integration_time=counted_file_parser.get_scan_integration_time()
		self.scan_close_shutter=counted_file_parser.get_scan_close_shutter()
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
		s=self.filename+'\n'
		q='( '+' '.join(self.scan_label.split('\n'))+' )'
		s+=q+'\n'
		s+='%d loops, %d points per loop. ' % (self.scan_nloops, self.scan_npoints)
		s+='Integration time of %ds. ' % (self.scan_integration_time)
		if self.scan_close_shutter: s+='Tried to close the shutter at end of scan. '
		s+='\n'
		if self.scan_dont_move:
			s+='Motor controllers were all stationary'
		else:
			s+='Moved MC%d from %.5fmm to %.5fmm.' % (self.scan_motor_controller+1, self.scan_start_postion, self.scan_stop_position)
		return s
		
	def set_patterns(self, pattern_labels):
		''' set the patterns '''
		self.pattern_labels=pattern_labels
		self.patterns=qy.hardware.counting.parser.parse_pattern_list(pattern_labels)
		self.curves=[]
		for i in range(len(pattern_labels)):
			c=curve(self.pattern_labels[i], self.patterns[i], self.scan_npoints, self.scan_nloops)
			self.curves.append(c)
	
	def read_chunk(self):
		''' read a chunk of data '''
		if not self.file_open: 
			counted_file_parser.open_counted_file(self.filename)
			counted_file_parser.read_metadata()
			self.file_open=True
			
		# read the chunk
		triplet_count=counted_file_parser.read_chunk()
				
		# send all the rates to the curves
		for curve in self.curves:
			rate=0
			pattern=curve.pattern
			if pattern[1]==1: rate=counted_file_parser.get_fpga_rate(pattern[0])
			if pattern[1]==2: rate=counted_file_parser.get_number_rate(*pattern[0])
			if pattern[1]==3: rate=counted_file_parser.get_special_rate(len(pattern[0]))
			position=counted_file_parser.get_motor_controller_position(self.scan_motor_controller)
			step=counted_file_parser.get_scan_step()
			loop=counted_file_parser.get_scan_loop()
			curve.add_rate(step, loop, position, rate)
		
		return triplet_count
		