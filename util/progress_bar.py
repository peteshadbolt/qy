import sys

def progress_bar(progress):
    ''' progress bar '''
    t=int(100*progress)
    sys.stdout.write('\r[{0}] {1}%'.format('#'*(t/10), t))
