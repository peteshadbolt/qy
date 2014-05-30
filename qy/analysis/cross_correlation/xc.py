import cross_correlate as c
from glob import glob
from matplotlib import pyplot as plt
import argparse

# Set up the command line parser
parser = argparse.ArgumentParser(description='Cross-correlate')
parser.add_argument('dpc_file',  type=str, nargs='?', default='MEASURE', help='The filename of an SPC file to process. If no filename is provided, I will try to connect to the DPC230 and measure.')
parser.add_argument('pattern',  type=str, nargs='+', help='A start/stop pair, e.g. "AB"')
parser.add_argument('-t',  '--integration_time', metavar='integration_time', default=2, type=float, help='Integration time, in seconds')
parser.add_argument('-w',  '--histogram_width', metavar='histogram_width', default=20, type=float, help='Histogram width, in ns')
parser.add_argument('-g',  '--make_graph', metavar='make_graph', nargs='?', const=True, default=False, type=bool, help='Should I make a graph?')
args = parser.parse_args()


# Do cross-correlation
c.set_integration_time(args.integration_time)
c.set_histogram_width(args.histogram_width)

'''
# Plot each curve requested
for start, stop in args.pattern:
    data=c.cross_correlate(args.dpc_file, start, stop)
    plt.plot(data['times'], data['counts'], 'k-')

# Finish the plot
plt.grid(ls='-', color='#dddddd', which='major')
plt.xlabel('Delay')
plt.yticks([])
plt.gca().set_axisbelow(1)
plt.savefig('xc.pdf')
'''
