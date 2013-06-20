import numpy as np
import sys

def dict_to_sorted_numpy(x):
    ''' convert a dictionary to a sorted numpy array '''
    data=sorted(x.items(), key=lambda x:x[0])
    return np.array([list(item[0])+[item[1]] for item in data])

def get_key(filename): return '_'.join(os.path.split(filename)[-1].split('.')[0].split('_')[:-1])

def get_groups(directory):
    '''directory'''
    files=map(lambda x: os.path.join(directory, x), os.listdir(directory))
    keys=list(set(map(get_key, files)))
    groups={k:[] for k in keys}
    for file in files:
        groups[get_key(file)].append(file)
    return groups

last_t=0

def progress_bar(progress, divisor=None):
    ''' progress bar '''
    global last_t

    if divisor==None: 
        t=int(100*progress)
    else:
        t=int(100*progress/float(divisor-1))

    if t<=0 or t>last_t:
        last_t=t
        sys.stdout.write('\r[{0}] {1}%'.format('#'*(t/5), t))
        sys.stdout.flush()
    if t==100: 
        sys.stdout.write('\r')
        sys.stdout.flush()
        print
