
'''
This code manages conversion of raw FIFO data from the DPC230 card into meaningful timetags.
It connects to spcm32x64.dll in simulation mode, allowing the postprocessing stage to be run in parallel with data aquisition.
'''

from ctypes import *
import sys, time, os
import qy

def nocallback(s): pass

class dpc_post:
	def __init__(self, callback=None):
		''' Constructor '''
		# connect to the DLL
		self.dll_path=qy.settings.lookup('dll_path')
		self.spc=CDLL(os.path.join(self.dll_path, 'spcm32x64.dll'))
		
		self.callback=nocallback if callback==None else callback		
		self.refresh_rate=0.2
		self.connect_to_dll()
		
	def connect_to_dll(self, ini_file=None):
		''' Initializes spcm32x64.dll in simulation mode. Pass the name of the INI configuration file to use. '''
		if ini_file==None: ini_file=os.path.join(self.dll_path, 'simulate.ini')
		ini_file_c=create_string_buffer(ini_file, 256)	# ctypes ini name
		ret = self.spc.SPC_init(ini_file_c)				# connect to the board
				
		# if the return code is <0, we couldn't initialize the board for some reason
		if ret<0:
			print 'error: python couldn\'t initialize spcm32x64.dll'
			sys.exit(0)
		else:
			pass
			#print 'initialized the spcm32x64.dll OK. using INI file "%s"' % os.path.split(ini_file)[1]
		return ret
		
	def kill(self):
		''' kill '''
		self.spc.SPC_close()
		
	def convert_raw_data(self, tdc1_filename, tdc2_filename):
		''' converts a raw FIFO data file to SPC format '''
			
		# initialize photon streams
		tdc1_stream_hndl=self.init_phot_stream(tdc1_filename, 1)
		tdc2_stream_hndl=self.init_phot_stream(tdc2_filename, 2)
		
		# prepare for conversion
		if tdc1_stream_hndl.value<0 or tdc2_stream_hndl.value<0: print 'error loading raw data streams'; sys.exit(0)
		spc_file=os.path.join(os.path.dirname(tdc1_filename), 'photons.spc')
		
		# empty the spc file
		q=open(spc_file, 'wb')
		q.write('')
		q.close()
		
		spc_file=c_char_p(spc_file)
		max_per_call=c_int(int(4e6))		# how many?
		
		# initialize and convert first chunk
		self.callback('Converting raw data...')
		ret=self.spc.SPC_convert_dpc_raw_data(tdc1_stream_hndl, tdc2_stream_hndl, c_short(1), spc_file, max_per_call)
		
		# convert remaining chunks
		while ret>0: 
			ret=self.spc.SPC_convert_dpc_raw_data(tdc1_stream_hndl, tdc2_stream_hndl, c_short(0), spc_file, max_per_call)
			self.callback('Converting raw data...')
		self.callback('Finished converting raw data.')
		
		# check for errors
		if ret<0: 
			self.callback('Error converting raw data file to SPC format')
			print 'Error converting raw data file to SPC format';	sys.exit(0)
				
		# close streams
		self.spc.SPC_close_phot_stream(tdc1_stream_hndl)
		self.spc.SPC_close_phot_stream(tdc2_stream_hndl)

		# empty those files to save space
		f=open(tdc1_filename, 'wb'); f.close()
		f=open(tdc2_filename, 'wb'); f.close()
		
		# return the name of the new spc file
		return spc_file.value

	#################################
	# other functions               #
	#################################
	
	def init_phot_stream(self, spc_filename, which_tdc):
		''' initiate a photon stream for conversion to spc format '''
		fifo_type=c_short(8)
		spc_file=c_char_p(spc_filename)
		
		files_to_use=c_short(0)
		stream_type=(1<<which_tdc) ^ (1<<3) ^ (1<<8) ^ (1<<10)
		stream_type=c_short(stream_type)
		what_to_read=1
		what_to_read=c_short(what_to_read)
		ret = self.spc.SPC_init_phot_stream(fifo_type, spc_file, files_to_use, stream_type, what_to_read)
		return c_short(ret)