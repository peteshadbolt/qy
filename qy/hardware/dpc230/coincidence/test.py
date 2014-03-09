from ctypes import *
import os

#f.restype = ctypes.POINTER(ctypes.c_int * 10)

class CountRate(Structure):
    _fields_ = [('pattern', c_short), 
                ('count', c_long)]

def binary_pattern_to_alphanumeric(pattern):
    ''' Convert a binary-encoded detection event to an alphanumeric string'''
    alphabet='abcdefghijklmnop'
    letters = [alphabet[i] for i in range(16) if (1<<i & pattern)>0]
    return ''.join(letters)

os.system('gcc -shared -o coincidence.so coincidence.c')
coincidence = CDLL('coincidence.so')
coincidence.process_spc.restype=POINTER(CountRate)
coincidence.get_nonzero_pattern_count.restype=c_int
coincidence.set_window(-1)
coincidence.set_time_cutoff_ms(5000)
delays = c_int * 16
coincidence.set_delays(delays(10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
coincidence.show_delays()
data = coincidence.process_spc('minute.spc')

data_dict={}
for i in range(coincidence.get_nonzero_pattern_count()):
    label=binary_pattern_to_alphanumeric(data[i].pattern)
    data_dict[label] = data[i].count

coincidence.reset()



print data_dict
