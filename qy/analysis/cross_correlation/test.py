import cross_correlate as c
from glob import glob
import re
import numpy as np
from matplotlib import pyplot as plt

filename=glob('/home/pete/physics/projects/test_data/minute.spc')[0]

# Do cross-correlation
c.set_time_cutoff(60)
c.set_histogram_bins(1000)
data=c.cross_correlate(filename, 0, 1)

# Plot
plt.plot(data['times'], data['counts'], 'k-')
#plt.xticks(np.linspace(0, 12.5*10, 11))
plt.grid()
plt.savefig('out.pdf')
