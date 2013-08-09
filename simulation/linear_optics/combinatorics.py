from scipy.misc import comb

def choose(n,r):
    out=1;
    if (n<r): return 0
    for i in range(1, n-r+1):
        out *= (i+r)/float(i)
    return int(out+.5)

def fromindex(idx, p, m):
    mx = choose(m+p-1,p)
    if idx>=mx: print 'Index out of range'; return
    n=m+p-1
    r=p
    i = 0; y = 0
    modes = [0]*p
    idx = mx-idx-1

    while n>0:
        if n>r and r>=0:
            y = choose(n-1,r)
        else:
            y = 0
        if idx>=y:
            idx = idx-y
            modes[i] = m+p-1-n-i
            r+=-1
            i+=1
        n+=-1;
    return modes

def toindex(modes, p, m):
    out=0
    mx = choose(m+p-1,p)
    for i in range(1, p+1):
        out+=choose(m-modes[p-i]+i-2,i)
    return mx-out-1

