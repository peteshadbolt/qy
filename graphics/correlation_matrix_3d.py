import numpy as np
import colorsys
import os, subprocess

''' this module is used for plotting 3d correlation matrices '''

def render(filename, scaling=2, display=True):
	''' call povray '''
	w, h=(640*scaling,480*scaling)
	print 'rendering POVray 3d image %s (%d x %d)...' % (filename, w,h),
	
	root, file=os.path.split(filename)
	image_filename=os.path.join(root, file)

	output='Output_File_Name=%s.png' % image_filename
	args=[r'C:\Program Files\megapov\bin\megapov.exe', filename, '+FN', '+H%d' % h, '+W%d' % w, 'Antialias=On', output]
	out=open(os.devnull, 'w'); err=open(os.devnull, 'w')
	p=subprocess.Popen(args, stdout=out, stderr=err)
	out.close(); err.close()
	p.wait()
	print 'done'
	
def sphere(x,y,z,r,color=1):
	''' generate povray code for a sphere at a point in space and with a certain radius '''
	R,G,B=colorsys.hsv_to_rgb(color, 1, 1)
	#R,G,B=1,0,0
	q=(x,y,z,r, R,G,B)
	return 'sphere {<%.9f, %.9f, %.9f> %.9f pigment{color rgb <%.5f,%.5f,%.5f>}}\n' % q

def plot3d(matrix, filename='out.pov', template='3d', color=None, scale=2, normalization=None):	
	''' generates povray code for a 3d image of the cube '''
	# get the template
	path=os.path.join(os.path.split(__file__)[0], 'templates/povray_template_%s.pov' % (template))
	f=open(path, 'r')
	output=f.read()+'\n'
	f.close()
	
	# generate all spheres
	X,Y,Z = matrix.shape
	
	# perhaps?
	#matrix=np.sqrt(matrix)
	
	xs=2./(X-1); ys=2./(Y-1); zs=2./(Z-1)
	n=scale*.5*xs/np.amax(matrix)
	
	c=1/np.amax(matrix)
	
	if normalization!=None: n=normalization
	
	for x in range(X):
		for y in range (Y):
			for z in range(Z):
				output+=sphere(x*xs-1,y*ys-1,z*zs-1, matrix[x,y,z]*n, c*matrix[x,y,z] if color==None else color)
		
	# finish off
	f=open(filename, 'w')
    f.write(output)
    f.close()
	render(filename)
