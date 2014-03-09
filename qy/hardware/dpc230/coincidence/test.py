from ctypes import *

coincidence = CDLL('coincidence.so')
coincidence.set_window(20)
coincidence.process_spc('minute.spc')
