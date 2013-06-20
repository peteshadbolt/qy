import sys

def progress_bar(progress, divisor=None):
    ''' progress bar '''
    t=0
    if divisor==None: 
        t=int(100*progress)
    else:
        t=int(100*progress/float(divisor-1))
    sys.stdout.write('\r[{0}] {1}%'.format('#'*(t/10), t))
