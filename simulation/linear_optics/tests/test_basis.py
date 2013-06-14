from scipy.misc import comb
import numpy as np
from qy.simulation import linear_optics as lo
from qy.simulation import combinadics

def largestv(a,b,x):
    ''' largest value v where v < a and (v choose b <= x) '''
    v = a - 1
    #print v, b, x
    while comb(v, b, exact=True) > x:
        v+=-1
    return v

def element(n,k,m):
    ''' return the mth lexicographic element of combination C(n,k) '''
    ans=np.zeros(k, dtype=int)
    a=n*1
    b=k*1
    
    # x is the dual of m
    x=(comb(n, k, exact=1)-1)-m

    for i in range(k):
        ans[i]=largestv(a,b,x)
        x=x-comb(ans[i],b,exact=True)
        a=ans[i]
        b=b-1

    for i in range(k):
        ans[i]= (n-1)-ans[i]

    return ans

from time import clock

for i in range(10):
    print element(5,3,i)
    print combinadics.fock(5,3,i)

t=clock()
for i in range(10):
    for j in range(10000):
        a=element(5,3,i)
print clock()-t



t=clock()
for i in range(10):
    for j in range(10000):
        a=combinadics.fock(5,3,i)
print clock()-t
    



