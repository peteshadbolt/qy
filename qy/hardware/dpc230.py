from ctypes import *
import sys, time, os
import qy.settings

param_names_list=['CFD_LIMIT_LOW','CFD_LIMIT_HIGH','CFD_ZC_LEVEL','CFD_HOLDOFF',
        'SYNC_ZC_LEVEL','SYNC_FREQ_DIV','SYNC_HOLDOFF','SYNC_THRESHOLD',
        'TAC_RANGE','TAC_GAIN','TAC_OFFSET','TAC_LIMIT_LOW',
        'TAC_LIMIT_HIGH','ADC_RESOLUTION','EXT_LATCH_DELAY','COLLECT_TIME',
        'DISPLAY_TIME', 'REPEAT_TIME','STOP_ON_TIME','STOP_ON_OVFL',
        'DITHER_RANGE','COUNT_INCR','MEM_BANK','DEAD_TIME_COMP',
        'SCAN_CONTROL','ROUTING_MODE','TAC_ENABLE_HOLD','MODE',
        'SCAN_SIZE_X','SCAN_SIZE_Y','SCAN_ROUT_X','SCAN_ROUT_Y',
        'SCAN_POLARITY','SCAN_FLYBACK','SCAN_BORDERS','PIXEL_TIME',
        'PIXEL_CLOCK','LINE_COMPRESSION','TRIGGER','EXT_PIXCLK_DIV',
        'RATE_COUNT_TIME','MACRO_TIME_CLK','ADD_SELECT','ADC_ZOOM',
        'XY_GAIN','IMG_SIZE_X','IMG_SIZE_Y','IMG_ROUT_X',
        'IMG_ROUT_Y','MASTER_CLOCK','ADC_SAMPLE_DELAY','DETECTOR_TYPE',
        'X_AXIS_TYPE','CHAN_ENABLE','CHAN_SLOPE','CHAN_SPEC_NO']

param_id_dict=dict(zip(map(str.lower, param_names_list), range(len(param_names_list))))

class spcmodinfo(Structure):
    _fields_=[('module_type', c_short),
              ('bus_no', c_short),
              ('slot_no', c_short),
              ('in_use', c_short),
              ('init', c_short),
              ('base_adr', c_ushort)]
              
class spcrates(Structure):
    _fields_=[('sync_rate', c_float),
              ('cfd_rate', c_float),
              ('tac_rate', c_float),
              ('adc_rate', c_float)]

spcinfo_comments=['base I/O address on PCI bus', 'set to initialisation result code', '= CFD_TH1 threshold of CFD1', 
                '= CFD_TH2 threshold of CFD2', '= CFD_TH3 threshold of CFD3', '= CFD_TH4 threshold of CFD4', 
                '= CFD_ZC1 Zero Cross level of CFD1', '= CFD_ZC2 Zero Cross level of CFD2', '= CFD_ZC3 Zero Cross level of CFD3', 
                'DPC range in TCSPC and Multiscaler mode', '1,2,4', 'not used for DPC230', 
                'TDC offset in TCSPC and Multiscaler mode', 'not used for DPC230', '= CFD_ZC4 Zero Cross level of CFD4', 
                'no of points of decay curve', 'not used for DPC230', '0.0001 .. 100000s , default 2.0s', 
                'not used for DPC230', 'not used for DPC230', '1 (stop) or 0 (no stop)', 
                'not used for DPC230', 'not used for DPC230', 'not used for DPC230', 
                'DPC/TDC active', 'not used for DPC230', 'not used for DPC230', 
                'DPC230  bits 0-7 - control bits', 'macro time clock in ps', 'module no on PCI bus ( 0-7)', 
                'module\'s operation mode', 'not used for DPC230', 'not used for DPC230', 
                'not used for DPC230', 'not used for DPC230', 'not used for DPC230', 
                'not used for DPC230', 'not used for DPC230', 'source of pixel clock in Image modes', 
                'not used for DPC230', 'external trigger condition', 'not used for DPC230', 
                'not used for DPC230', 'rate counting time in sec', 'not used for DPC230', 
                'not used for DPC230', 'EEPROM', 'not used for DPC230', 
                'not used for DPC230', 'not used for DPC230', 'not used for DPC230', 
                'not used for DPC230', 'not used for DPC230', 'not used for DPC230', 
                'not used for DPC230', 'type of active inputs', 'not used for DPC230', 
                'enable(1)/disable(0) input channels', 'active slope of input channels', 'channel numbers of special inputs']



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


def nocallback(s): pass

class dpc230:
    ''' Provides an interface to spcm32x64.dll, pulling timetags off the DPC230 time tagger.  '''
    def __init__(self, mode, callback=None):
        ''' Constructor '''
        # Set up
        self.mode=mode
        self.callback=callback if callback!=None else nocallback
        self.callback('Connecting to DPC-230...')
        
        # We only have one card at the moment, so we always communicate with card #0
        self.module_no=c_short(0)
        
        # Create the photon buffer
        self.buffer_frames=int(1e6)                                 # one million photons ought to do it!
        self.buffer_words=self.buffer_frames*2                      # each photon is a word
        self.buffer_bytes=self.buffer_words*2                       # each photon is a word
        self.photon_buffer=create_string_buffer(self.buffer_bytes+10)
                
        # Connect to the DLL
        self.dll_path=qy.settings.get('dpc230.dll_path')
        self.spc=CDLL(os.path.join(self.dll_path, 'spcm32x64.dll'))
        
        # Set vars
        self.refresh_rate=0.3 # Important for reading off disk
        
        # Initialize
        if self.mode=='hardware':
            self.init_hardware_mode()
        else:
            self.init_software_mode()
        
    ###########################
    # really useful functions #
    ###########################
            

    def count(self, collect_time=1, file_buffer=None):
        ''' 
        Acquires data from the card for the chosen collection time, writes raw FIFO data to disk
        Returns the path of the output SPC photon file, ready for coincidence counting.
        '''
        # Automatically choose a buffer
        if file_buffer==None:
            file_buffer=self.photon_buffer_2 if self.photon_buffer_switch else self.photon_buffer_1
            self.photon_buffer_switch = not self.photon_buffer_switch
        
        # We want to write data into two files in the target directory
        tdc1_filename=os.path.join(file_buffer, 'tdc1.raw')
        tdc2_filename=os.path.join(file_buffer, 'tdc2.raw')
        
        # Get ready for measurement
        tdc1_file=open(tdc1_filename, 'wb')
        tdc2_file=open(tdc2_filename, 'wb')
        self.clear_rates()
        both_armed=True
        total=0
        measurement_time=time.clock()
        self.set_parameter('collect_time', collect_time)

        # Start the measurement
        self.start_measurement()
        #self.callback('Collecting photons...')
        
        # Keep grabbing data and dumping it to the file
        while both_armed:
            # see whether there is any data in the fifos, if so grab a chunk and write to disk
            empty=self.fifos_empty()
            if not empty[0]: self.read_fifo_chunk(0, tdc1_file)
            if not empty[1]: self.read_fifo_chunk(1, tdc2_file)
            both_armed=self.both_fifos_armed()

            if time.clock()-measurement_time > self.refresh_rate:
                rates=self.read_rates()
                total=int(rates.sync_rate+rates.cfd_rate)
                total=format(total, ",d")
                actual_collection_time=self.get_actual_coltime()
                stay_alive=self.callback('%s photons/s (%.2fs)' % (total,actual_collection_time))
                if stay_alive==False: both_armed=False
                measurement_time=time.clock()
            
        # Collect the last photons and tidy up
        empty=self.fifos_empty()
        if not empty[0]: self.read_fifo_chunk(0, tdc1_file)
        if not empty[1]: self.read_fifo_chunk(1, tdc2_file)
        self.stop_measurement()
        tdc1_file.close()
        tdc2_file.close()
                
        # Return the filenames of the two photon buffers
        self.callback('%s photons/s (%.2fs)' % (total, 0))
        return tdc1_filename, tdc2_filename
        

    def kill(self):
        ''' we have finished '''
        self.spc_close()
        
    #################################
    # initialization functions      #
    #################################
        

    def connect_to_board(self, ini_file=None):
        ''' Initializes the time tagger. Pass the name of the INI configuration file to use. '''
        if ini_file==None: ini_file=os.path.join(self.dll_path, 'spcm.ini')
        ini_file_c=create_string_buffer(ini_file, 256)  # ctypes ini name
        ret = self.spc.SPC_init(ini_file_c)             # connect to the board
                
        # if the return code is <0, we couldn't initialize the board for some reason
        if ret<0:
            self.callback('Error connecting to DPC-230!')
        else:
            self.callback('Initialized the DPC-230 OK, using INI file "%s"' % os.path.split(ini_file)[1])
        return ret


    def init_software_mode(self, ini_file=None):
        ''' Initializes spcm32x64.dll in simulation mode. Pass the name of the INI configuration file to use. '''
        if ini_file==None: ini_file=os.path.join(self.dll_path, 'simulate.ini')
        ini_file_c=create_string_buffer(ini_file, 256)  # ctypes ini name
        ret = self.spc.SPC_init(ini_file_c)             # connect to the board
                
        # if the return code is <0, we couldn't initialize the board for some reason
        if ret<0:
            print 'error: python couldn\'t initialize spcm32x64.dll'
            sys.exit(0)
        else:
            self.callback('Initialized the DPC-230 OK, using INI file "%s"' % os.path.split(ini_file)[1])
        return ret

        
    def init_hardware_mode(self):
        ''' Initialize the system in hardware control mode '''
        # Connect to the board. Be robust!
        self.connect_to_board()
        if self.get_init_status()==-6: 
            if qy.settings.get('dpc.force_connection'):
                # TODO: this is still dodgy. Why can't we close the connection?
                print 'Forcing connection to DPC230 ... (enable/disable using qy.settings)'
                self.set_mode(0, 1)
                self.kill()
                self.connect_to_board()
                if self.get_init_status()==-6: 
                    self.callback('Still failed to connect :(')
                    sys.exit(0)
            else:
                sys.exit(0)

        # Figure out where we should put timetags
        # IMPORTANT! These paths MUST point to RAMDISKS!!!!!!
        self.photon_buffer_switch=False
        self.photon_buffer_1=qy.settings.get('photon_buffer_1')
        self.photon_buffer_2=qy.settings.get('photon_buffer_2')
    
        # Set up the discriminators etc.
        self.set_parameter('collect_time', 1)
        self.set_parameter('mem_bank', 6)
        self.set_parameter('mode', 8)
        self.set_parameter('detector_type', 6)
        self.set_parameter('chan_enable', 1044735)
        self.set_parameter('chan_slope', 1044735)

        
    def get_init_status(self):
        ''' gets the initialization status of the board '''
        ret=self.spc.SPC_get_init_status(self.module_no);
        if ret<0: self.callback('Warning: unexpected spc init status. \n\
This usually means that another process has control of the DPC-230.')
        return ret
            

    def get_module_info(self):
        ''' gets loads of info about the board as a string '''
        info=spcmodinfo()
        self.spc.SPC_get_module_info(self.module_no, byref(info));
        s='Module info:\n'
        s+='  type: %d\n' % info.module_type
        s+='  bus number: %d\n' % info.bus_no
        s+='  in use: %s\n' % decode_boolean(info.in_use)
        init_desc='error' if info.init<0 else 'no error'
        s+='  initialization result code: %d [%s]\n' % (info.init, init_desc)
        s+='  PCI bus bus I/O address: %s\n' % info.base_adr
        return s
        

    def test_id(self):
        ''' gets the serial number of the board: should be 230 as this is a DPC-230'''
        ret=self.spc.SPC_test_id(self.module_no);
        return ret
        

    def get_mode(self):
        ''' determine which DLL mode we are in: should be 0, indicating hardware mode '''
        ret=self.spc.SPC_get_mode();
        return ret
        

    def set_mode(self, mode=0, force_use=0):
        ''' 
        set which DLL mode we are in: should be 0, indicating hardware mode 
        '''
        mode_c=c_short(mode)
        force_use_c=c_short(force_use)
        in_use_c=c_int(1)
        ret=self.spc.SPC_set_mode(mode_c, force_use_c, byref(in_use_c));
        return ret
        

    def get_board_summary(self):
        ''' pretty-prints a summary of the status of the initialized board '''

        s='DPC230 interface, %s mode\n' % self.mode
        s +=  'Board info:\n'
        s+= '  init status: %d\n' % self.get_init_status()
        s+= '  genuine DPC-230 board\n' if self.test_id()==230 else 'warning: something about this board is fishy\n'
        mode=self.get_mode()
        mode_desc='hardware' if mode==0 else 'warning: simulation'
        s+= '  mode: %d [%s]\n' % (mode, mode_desc)
        s+= '\n'
        s+= self.get_module_info()
        s+= '\n'
        return s
        
    #################################
    # setup functions               #
    #################################


    def set_parameter(self, par_name, value):
        ''' writes a particular setup parameter '''
        par_id=param_id_dict[par_name]
        par_id_c=c_short(par_id)
        value_c=c_float(value)
        ret=self.spc.SPC_set_parameter(self.module_no, par_id_c, value_c);
        if ret!=0: print 'something went wrong when trying to write device parameter.'
        return ret
        

    def get_parameter(self, par_name):
        ''' reads a particular setup parameter '''
        par_id=param_id_dict[par_name]
        par_id_c=c_short(par_id)
        value_c=c_float(0.)
        ret=self.spc.SPC_get_parameter(self.module_no, par_id_c, byref(value_c));
        if ret!=0: print 'something went wrong when trying to read device parameter.'
        return value_c.value
        

    def get_setup_summary(self):
        ''' pretty-prints a summary of the setup parameters of the board. '''
        s= 'Setup info:'
        s+= '  operation mode:   %d [%s]' % (self.get_parameter('mode'), decode_operation_mode(self.get_parameter('mode'))) + '\n'
        s+= '  memory bank:      %d [%s]' % (self.get_parameter('mem_bank'), decode_memory_bank(self.get_parameter('mem_bank'))) + '\n'
        s+= '  detector type:    %s' % decode_detector_type(self.get_parameter('detector_type')) + '\n'
        s+= '  enabled channels:%s' % decode_chan_enable(int(self.get_parameter('chan_enable'))) + '\n'
        s+= '  channel slope:   %s' % decode_chan_enable(int(self.get_parameter('chan_slope'))) + '\n'
        s+= '  collection time:  %s' % self.get_parameter('collect_time') + '\n'
        s+= '  stop at end:      %s' % decode_boolean(self.get_parameter('stop_on_time')) + '\n'
        s+= '  time bin size:    %.20f fs' % (self.get_parameter('tac_enable_hold')*1e3) + '\n'
        return s


    def print_setup_summary(self):
        print self.get_setup_summary()
        
    #################################
    # status functions              #
    #################################
            

    def test_state(self):
        ''' sets a variable according to the current state of the measurement. controls the measurement loop '''
        state=c_short()
        ret = self.spc.SPC_test_state(self.module_no, byref(state))
        if ret!=0: print 'something went wrong when trying to test the system state.'
        return state.value
        

    def print_state(self):
        ''' sets a variable according to the current state of the measurement. controls the measurement loop '''
        state=self.test_state()
        s=''
        for pair in state_bits:
            if state & pair[0]: s+='%s / ' % pair[1]
        print s
        

    def fifos_armed(self):
        ''' tell us if the FIFOs are empty or not... '''
        state=self.test_state()
        return (state & 0x80!=0, state & 0x4000!=0)
        

    def both_fifos_armed(self):
        ''' tell us if both FIFOs are empty or not... '''
        state=self.test_state()
        return state&0x80!=0 and state&0x4000!=0
        

    def fifos_empty(self):
        ''' tell us if the FIFOs are empty or not... '''
        state=self.test_state()
        return (state & 0x100!=0, state & 0x200!=0)
        

    def get_sync_state(self):
        ''' In relative timing mode, tests for a signal in the reference channel '''
        sync_state=c_short(0)
        ret = self.spc.SPC_get_sync_state(self.module_no, byref(sync_state))
        if ret!=0: print 'something went wrong when trying to get the sync state.'
        return sync_state.value
                

    def get_time_from_start(self):
        ''' Reads the DPC collection timer '''
        time=c_float(0)
        ret = self.spc.SPC_get_time_from_start(self.module_no, byref(time))
        if ret!=0: print 'something went wrong when trying get the time from the start of the experiment.'
        return time.value
        

    def get_break_time(self):
        ''' Finds the moment of a measurement interrupt '''
        time=c_float(0)
        ret = self.spc.SPC_get_break_time(self.module_no, byref(time))
        if ret!=0: print 'something went wrong when trying get the break time.'
        return time.value
        

    def get_actual_coltime(self):
        ''' Actual collection time '''
        time=c_float(0)
        ret = self.spc.SPC_get_actual_coltime(self.module_no, byref(time))
        if ret!=0: print 'something went wrong when trying get the collection time.'
        return time.value
        

    def read_rates(self):
        ''' Reads photon rate counts, calculates rate values '''
        rates=spcrates()
        ret = self.spc.SPC_read_rates(self.module_no, byref(rates))
        if ret!=0: print 'something went wrong when trying to read rates.'
        return rates
        

    def print_rates(self):
        ''' Pretty prints photon count rates '''
        rates=self.read_rates()
        s='TDC1 rate: %.0f' % rates.sync_rate
        s+=' / TDC2 rate: %.0f' % rates.cfd_rate
        print s
        

    def clear_rates(self):
        ''' Clears all rate counters '''
        ret = self.spc.SPC_clear_rates(self.module_no)
        if ret!=0: print 'something went wrong when trying to clear count rates'
        return ret
        

    def get_fifo_usage(self):
        ''' Tells us how full the FIFO is - a float between 0 and 1 '''
        usage_degree_1=c_float()
        ret = self.spc.SPC_get_fifo_usage(c_short(0), byref(usage_degree_1))
        if ret!=0: print 'something went wrong when trying to read the fifo usage'
        usage_degree_2=c_float()
        ret = self.spc.SPC_get_fifo_usage(c_short(8), byref(usage_degree_2))
        if ret!=0: print 'something went wrong when trying to read the fifo usage'
        return usage_degree_1.value, usage_degree_2.value
        
    #################################
    # measurement control functions #
    #################################
        

    def start_measurement(self):
        ''' Clears FIFO and buffers, and arms active TDCs '''
        ret = self.spc.SPC_start_measurement(self.module_no)
        if ret!=0: print 'something went wrong when trying to start the measurement.'
        return ret
        

    def stop_measurement(self):
        ''' Stops the measurement '''
        ret = self.spc.SPC_start_measurement(self.module_no)
        if ret!=0: print 'something went wrong when trying to start the measurement.'
        return ret
        
    #################################
    # memory transfer functions     #
    #################################
    

    def read_fifo(self, which_tdc, count):
        ''' Reads photon time tags from the FIFO into memory, returns the number of 16 bit words read '''
        count_c=c_long(count)
        module_c=c_short(0) if which_tdc==0 else c_short(8)
        ret = self.spc.SPC_read_fifo(module_c, byref(count_c), byref(self.photon_buffer))
        if ret!=0: print 'something went wrong when trying to read a FIFO.'
        return count_c.value
        

    def spc_close(self):
        ''' Close the connection to the DPC230 '''
        self.spc.SPC_close()
        self.callback('Closed connection to DPC230')
        
    #################################
    # other functions               #
    #################################
        

    def read_fifo_chunk(self, which, target):
        ''' read a chunk of data from a FIFO '''
        nwords=self.read_fifo(which, self.buffer_words)
        bytes=self.photon_buffer.raw[:nwords*2]
        target.write(bytes)
        
    #################################
    # conversion functions          #
    #################################
        

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
        max_per_call=c_int(int(4e6))        # how many?
        
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
            print 'Error converting raw data file to SPC format';   sys.exit(0)
                
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
        max_per_call=c_int(int(4e6))        # how many?
        
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
            print 'Error converting raw data file to SPC format';   sys.exit(0)
                
        # close streams
        self.spc.SPC_close_phot_stream(tdc1_stream_hndl)
        self.spc.SPC_close_phot_stream(tdc2_stream_hndl)

        # empty those files to save space
        f=open(tdc1_filename, 'wb'); f.close()
        f=open(tdc2_filename, 'wb'); f.close()
        
        # return the name of the new spc file
        return spc_file.value



    def __str__(self):
        ''' Return a string, describing state '''
        return self.get_board_summary()+self.get_setup_summary()


if __name__=='__main__':
    x=dpc230('hardware')

