import numpy as np
import colorsys
import os, subprocess
from matplotlib import pyplot as plt
import matplotlib.image as mpimg

''' this module is used for plotting 3d density matrices '''

def color_map(x, bright=1):
		''' maps a number (-1 to 1) to a color '''
		q=(255,(1-x)*155+20,(1-x)*155+10) if x>0 else ((1+x)*155+20,(1+x)*155+10,255)
		return tuple([a/255. for a in q])

def render(filename, scaling=1.5):
	''' call povray '''
	w, h=(320*scaling,240*scaling)
	print 'rendering POVray 3d image %s (%d x %d)...' % (filename, w,h),
	root, file=os.path.split(filename)
	image_dir=root
	#image_dir=os.path.join(root, 'images')
	#if not os.path.exists(image_dir): os.makedirs(image_dir)
	image_filename=os.path.join(image_dir, file)
	output='Output_File_Name=%s.png' % image_filename
	args=[r'C:\Program Files\megapov\bin\megapov.exe', filename, '+FN', '+H%d' % h, '+W%d' % w, 'Antialias=On', output]
	
	p=subprocess.Popen(args)
	p.wait()
	
	# overlay
	img=mpimg.imread(image_filename+'.png')
	plt.imshow(img)
	plt.axis('off')
	plt.figtext(0.285,0.22,r'$0$', fontsize=20, ha='center', va='center')
	plt.figtext(0.41,0.14,'$1$', fontsize=20, ha='center', va='center')
	plt.figtext(0.74,0.22,'$0$', fontsize=20, ha='center', va='center')
	plt.figtext(0.61,0.14,'$1$', fontsize=20, ha='center', va='center')
	qq=filename.split('.')[0]
	#os.system('del %s' % filename)
	#os.system('del %s.png' % filename)
	#os.system('del %s.bak' % filename)
	plt.savefig('%s.png' % qq, bbox_inches='tight', dpi=50)
	
def plot_density_matrix_3d(matrix, filename='out.pov'):	
	''' generates povray code for a 3d image of the cube '''
	# get the template
	if not filename.endswith('.pov'): filename+='.pov'
	path=os.path.join(os.path.split(__file__)[0], 'templates/template.pov')
	f=open(path, 'r')
	output=f.read()+'\n'
	f.close()
	
	for i in range(2):
		for j in range(2):
			output+='object { column '
			output+='translate <%d, %d, 0> ' % (i,j)
			output+='pigment {color rgbf <%.2f,%.2f,%.2f,.1>} ' % color_map(matrix[i,j])
			output+='scale <1,1,%.4f>}\n' % matrix[i,j]

	# finish off
	f=open(filename, 'w');	
	f.write(output);	
	f.close()
	render(filename)