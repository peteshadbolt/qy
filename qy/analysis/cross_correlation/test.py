import cross_correlate as c
from glob import glob
from matplotlib import pyplot as plt
import argparse
import os
import json

# Set up the command line parser
parser = argparse.ArgumentParser(description='Cross-correlate')
parser.add_argument('dpc_file',  type=str, help='The filename of an SPC file to process')
parser.add_argument('pattern',  type=str, nargs='+', help='A start/stop pair, e.g. "AB"')
parser.add_argument('-t',  '--integration_time',default=0, type=float, help='Integration time, in seconds')
parser.add_argument('-w',  '--histogram_width', default=20, type=float, help='Histogram width, in ns')
parser.add_argument('-g',  '--make_graph', nargs='?', const=True, default=False, type=bool, help='Should I make a graph?')
parser.add_argument('-o',  '--output_filename', default=None, type=str, help='Where to write data/graphs')
args = parser.parse_args()

def compute_curves(dpc_file, patterns):
    ''' Get all the curves of interest '''
    alphabet='abcdefghijklmnop'
    lookup=dict(zip(alphabet, range(len(alphabet))))
    curves={}
    for start, stop in patterns:
        label=start+stop.lower()
        start=lookup[start.lower()]; stop=lookup[stop.lower()]
        curves[label]=c.cross_correlate(dpc_file, start, stop)
    return curves


def save(curves, filename):
    ''' Save to disk '''
    outfile=open(filename, 'w')
    json.dump(curves, outfile, indent=2)
    outfile.close()
    print 'Wrote %d cross-correlation curve%s to %s' % (len(curves), ' s'[len(curves)>1], filename)


def finish_axes(label=False):
    ''' Tidy up the current axes '''
    plt.grid(ls='--', color='#aaaaaa', which='major')
    plt.gca().set_axisbelow(1)
    plt.yticks([])
    w=args.histogram_width; ticks=[-w, -w/2., 0, w/2., w]
    if label:
        plt.xlabel('Delay, ns')
        plt.xticks(ticks)
    else:
        plt.xticks(ticks, ['']*3)


def plot(curves, filename):
    ''' Plot all the curves to a PDF file '''
    N=len(curves)
    plt.figure(figsize=(8, 2*N))
    for index, (label, curve) in enumerate(curves.items()):
        plt.subplot(N, 1, index+1)
        plt.plot(curve['times'], curve['counts'], '-', lw=1.5, color='#cc3333')
        plt.text(.02, .9, label.upper(), transform=plt.gca().transAxes)
        finish_axes(index==N-1)
    # Save
    plt.subplots_adjust(hspace=0)
    plt.savefig(filename)
    print 'Plotted a graph to %s' % filename


# Gubbins
if args.output_filename==None:
    root_filename=os.path.splitext(args.dpc_file)[0]
else:
    root_filename=args.output_filename

# Do cross-correlation
c.set_integration_time(args.integration_time)
c.set_histogram_width(args.histogram_width)
curves=compute_curves(args.dpc_file, args.pattern)

# Save to disk
save(curves, root_filename+'.json')

# Optionally, plot the graph
if args.make_graph: plot(curves, root_filename+'.pdf')
