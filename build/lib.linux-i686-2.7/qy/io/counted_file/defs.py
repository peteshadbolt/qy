####################################
# COUNTED FILE DEFS
###################################

alphabet_upper='ABCDEFGHIJKLMNOP'
alphabet_lower=alphabet_upper.lower()
alphabet=alphabet_upper

m = {1337: 'magic',
101: 'temporary_file',
102: 'stop_metadata',
103: 'scan_type',
201: 'scan_npoints',
202: 'scan_nloops',
203: 'scan_integration_time',
204: 'scan_close_shutter',
205: 'scan_dont_move',
206: 'scan_motor_controller',
207: 'scan_start_position',
208: 'scan_stop_position',
250: 'scan_label_nbytes',
301: 'motor_controller_update',
302: 'scan_loop',
303: 'scan_step',
304: 'integration_step',
305: 'stop_integrating',
401: 'start_count_rates',
402: 'count_rate',
403: 'stop_count_rates',
404: 'start_pause',
405: 'stop_pause'}
counted_file_label_map=dict([v,k] for k,v in m.items())
counted_file_label_map_invert=dict([k,v] for k,v in m.items())

FPGA=1
NUMBER=2
SPECIAL=3

def bitcount(x):
	c=0
	while x:
		x &= x -1
		c+=1
	return c
	
LOOKUP_BC = {i:bitcount(i) for i in range(0,17)}

GET_A = int('0000000000001111', 2)
GET_b = int('0000000011110000', 2)
GET_C = int('0000111100000000', 2)
GET_D = int('1111000000000000', 2)

def convert_number_pattern(pattern):
	a=LOOKUP_BC[(pattern & GET_A) >> 0]
	b=LOOKUP_BC[(pattern & GET_b) >> 4]
	c=LOOKUP_BC[(pattern & GET_C) >> 8]
	d=LOOKUP_BC[(pattern & GET_D) >> 12]
	return (a,b,c,d)
	
def match_fpga_to_number_pattern(number_pattern, fpga):
	data=convert_number_pattern(fpga)
	return number_pattern==data

####################################
# DPC_230 DEFS
###################################

param_names_list=['CFD_LIMIT_LOW','CFD_LIMIT_HIGH','CFD_ZC_LEVEL','CFD_HOLDOFF',
		'SYNC_ZC_LEVEL','SYNC_FREQ_DIV','SYNC_HOLDOFF','SYNC_THRESHOLD',
		'TAC_RANGE','TAC_GAIN','TAC_OFFSET','TAC_LIMIT_LOW',
		'TAC_LIMIT_HIGH','ADC_RESOLUTION','EXT_LATCH_DELAY','COLLECT_TIME',
		'DISPLAY_TIME',	'REPEAT_TIME','STOP_ON_TIME','STOP_ON_OVFL',
		'DITHER_RANGE','COUNT_INCR','MEM_BANK','DEAD_TIME_COMP',
		'SCAN_CONTROL','ROUTING_MODE','TAC_ENABLE_HOLD','MODE',
		'SCAN_SIZE_X','SCAN_SIZE_Y','SCAN_ROUT_X','SCAN_ROUT_Y',
		'SCAN_POLARITY','SCAN_FLYBACK','SCAN_BORDERS','PIXEL_TIME',
		'PIXEL_CLOCK','LINE_COMPRESSION','TRIGGER','EXT_PIXCLK_DIV',
		'RATE_COUNT_TIME','MACRO_TIME_CLK','ADD_SELECT','ADC_ZOOM',
		'XY_GAIN','IMG_SIZE_X','IMG_SIZE_Y','IMG_ROUT_X',
		'IMG_ROUT_Y','MASTER_CLOCK','ADC_SAMPLE_DELAY','DETECTOR_TYPE',
		'X_AXIS_TYPE','CHAN_ENABLE','CHAN_SLOPE','CHAN_SPEC_NO']

param_id_dict=dict([(param_names_list[i].lower(),i) for i in range(len(param_names_list))])

state_bits=((0x80, 'TDC1'), 
			(0x4000, 'TDC2'), 
			(0x80, 'measuring'), 
			(0x100, 'FIFO1 empty'), 
			(0x200, 'FIFO2 empty'), 
			(0x400, 'FIFO1 overflow'), 
			(0x800, 'FIFO1 overflow'), 
			(0x8, 'TDC1 timeout'), 
			(0x20, 'TDC2 timeout'), 
			(0x4, 'stopped'), 
			(0x2000, 'wait for frame signal to stop'), 
			(0x1000, 'wait for trigger'))
			
			
def decode_chan_enable(code):
	s=''
	for i in range(22):
		if i%4 == 0 : s+=' ' 
		s+='1' if (1<<i)&code>0 else '0'
		
	return s
	
def decode_operation_mode(mode):
	qq={6:'TCSPC FIFO', 7:'TCSPC FIFO', 8:'Absolute time FIFO mode', 9:'Absolute time FIFO Image mode'}
	return qq[mode]
	
def decode_memory_bank(bank):
	qq={6:'both DPCs active'}
	return qq[bank]
	
def decode_boolean(code):
	return 'yes' if code else 'no'
	
def decode_detector_type(type):
	if type==6: return '6 [LVTTL on TDC1&2]'
	return '%d [probably using some CFD inputs]' % type