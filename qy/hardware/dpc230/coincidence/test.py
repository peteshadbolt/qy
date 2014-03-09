from ctypes import *
import os


os.system('gcc -shared -o coincidence.so coincidence.c')
coincidence = CDLL('coincidence.so')
coincidence.set_window(20)
coincidence.set_time_cutoff_ms(5000)
delays = c_int * 16
coincidence.set_delays(delays(10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0))
coincidence.show_delays()
coincidence.process_spc('minute.spc')
