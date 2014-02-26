import numpy as np
import colorsys
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib import rc; rc('font', family='arial', size=10)
from matplotlib import cm

''' this module is used for plotting 3d correlation matrices '''


def distance_sorted(matrix):
	''' re-order by distance '''
	data=[]
	x,y,z=matrix.shape
	for i in range(x):
		for j in range(y):
			for k in range(z):
				mean=np.average([i,j,k])
				distance=(i-mean)**2+(j-mean)**2+(k-mean)**2
				data.append([distance, matrix[i,j,k]])
				
	data=sorted(data, key=lambda x: x[0])
	return np.array([q[1] for q in data])
	
def flatten(matrix):
	''' flatten the matrix '''
	x,y,z=matrix.shape
	x_values=range(x*y*z)
	m=matrix.reshape(x*y*z)
	return m

def correlation_matrix_comparison(m1, m2, filename='out.png', sort=False):	
	''' plots a correlation matrix in 2d '''
	figure=Figure(figsize=(10,5))
	canvas=FigureCanvas(figure)
	axes=figure.add_subplot(111)
	
	x,y,z=m1[0].shape
	x_values=range(x*y*z)
	
	# plot experiment
	correlation_matrix, name=m1
	m=distance_sorted(correlation_matrix) if sort else flatten(correlation_matrix)
	axes.bar(x_values, m, color='black')
	axes.text(0.02, 0.95, name, transform=axes.transAxes, ha='left', va='top')
		
	# plot theory
	correlation_matrix, name=m2
	m=distance_sorted(correlation_matrix) if sort else flatten(correlation_matrix)
	axes.bar(x_values, -m, color='black')
	axes.text(0.02, 0.05, name, transform=axes.transAxes, ha='left', va='bottom')
	
	# finish
	axes.set_xlabel('Correlation matrix (flattened) element index')
	axes.set_ylabel('Probability')
	canvas.print_figure(filename, dpi=100)