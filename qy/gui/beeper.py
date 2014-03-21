import winsound
		

def set_scaling_factor(rate):
    ''' Renormalize '''
    global scaling_factor
    if rate==0: return
    scaling_factor=center/rate
    
def beep(rate):
    ''' Call this function '''
    f=int(scaling_factor*rate)
    if f>max_f or f<min_f: 
        set_scaling_factor(rate)
        f=int(scaling_factor*rate)

    if f>0:
        winsound.Beep(int(f), 30)
		
min_f=800
max_f=10000
center=(max_f+min_f)/2.
set_scaling_factor(10000)
