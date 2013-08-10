import numpy as np
import sys

def dict_to_sorted_numpy(data):
    ''' convert a dictionary to a sorted numpy array '''
    N=len(data.keys()[0])
    sorted_data=sorted(data.items(), key=lambda pair:pair[0])
    structure=[('labels', int, (N,)), ('counts', float)]
    return np.array(sorted_data, dtype=structure)

#def copy_labelled_numpy_array(template):
    #''' return a copy of some labelled numpy data '''
    #out=np.copy(template)
    #return out

#def dict_to_sorted_numpy(x):
    #''' convert a dictionary to a sorted numpy array '''
    #data=sorted(x.items(), key=lambda x:x[0])
    #return np.array([list(item[0])+[item[1]] for item in data])

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

    if progress==0:
        sys.stdout.write('\r[{0}] {1}%'.format('#'*(t/5), t))
        sys.stdout.flush()
        last_t=t

    if t>last_t:
        last_t=t
        sys.stdout.write('\r[{0}] {1}%'.format('#'*(t/5), t))
        sys.stdout.flush()
    if t==100: 
        sys.stdout.write('\r')
        sys.stdout.flush()
        print

if __name__=='__main__':
    # test dict_to_sorted_numpy
    data={}
    data[(1,2,3)]=10
    data[(4,5,6)]=20
    data[(5,6,9)]=30
    data[(0,0,0)]=24.5
    print data
    
    n=dict_to_sorted_numpy(data)
    print n
    print n['counts']
    print n['labels']
    print n[:]

