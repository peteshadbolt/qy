import numpy as np
import colorsys
import os, subprocess

''' this module is used for plotting 3d correlation matrices '''

def render(pov_filename, scaling=2):
    ''' call povray '''
    w, h=(640*scaling,480*scaling)
    print 'rendering POVray 3d image %s (%d x %d)...' % (pov_filename, w,h),
    
    root, file=os.path.split(pov_filename)
    image_filename=os.path.join(root, file.split('.')[0])+'.png'

    print pov_filename
    print image_filename

    output='Output_File_Name=%s' % image_filename
    args=[r'C:\Program Files\megapov\bin\megapov.exe', pov_filename, '+FN', '+H%d' % h, '+W%d' % w, 'Antialias=On', output]
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

def plot3d(matrix, template_filename, pov_filename='out.pov', color=None, scale=2, normalization=None): 
    ''' generates povray code for a 3d image of the cube '''
    # load the template
    f=open(template_filename, 'r')
    output=f.read()+'\n'
    f.close()
    
    # generate all spheres
    X,Y,Z = matrix.shape
    
    # perhaps?
    #matrix=np.sqrt(matrix)
    
    xs=2./(X-1); ys=2./(Y-1); zs=2./(Z-1)
    if normalization == None:
        normalization=.1/np.amax(matrix)
    
    for x in range(X):
        for y in range (Y):
            for z in range(Z):
                if matrix[x,y,z]>0: 
                    output+=sphere(x*xs-1,y*ys-1,z*zs-1, matrix[x,y,z]*normalization*scale, color)
        
    # write the povray file
    f=open(pov_filename, 'w')
    f.write(output)
    f.close()
    render(pov_filename, scale)
