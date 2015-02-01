import numpy as np
import colorsys
import os
import subprocess

''' this module is used for plotting 3d correlation matrices '''


def render(pov_filename, scale=2):
    ''' call povray '''
    w, h = (640 * scale, 480 * scale)
    print 'povray %s (%d x %d)...' % (pov_filename, w, h),
    root, file = os.path.split(pov_filename)
    image_filename = os.path.join(root, file.split('.')[0]) + '.png'

    output = 'Output_File_Name=%s' % image_filename
    # args=[r'C:\Program Files\megapov\bin\megapov.exe', pov_filename, '+FN',
    # '+H%d' % h, '+W%d' % w, 'Antialias=On', output]
    args = [r'povray', pov_filename, '+FN', '+H%d' %
            h, '+W%d' % w, 'Antialias=On', output]
    out = open(os.devnull, 'w')
    err = open(os.devnull, 'w')
    # p=subprocess.Popen(args, stdout=out, stderr=err)
    p = subprocess.Popen(args)
    out.close()
    err.close()
    p.wait()
    print 'done'


def sphere(x, y, z, r, color=1):
    ''' generate povray code for a sphere at a point in space and with a certain radius '''
    if isinstance(color, tuple):
        R, G, B = color
    elif isinstance(color, float):
        R, G, B = colorsys.hsv_to_rgb(color, 1, 1)
    else:
        R, G, B = 1, 0, 0
    q = (x, y, z, r, R, G, B)
    return 'sphere {<%.9f, %.9f, %.9f> %.9f pigment{color rgb <%.5f,%.5f,%.5f>}}\n' % q


def plot3d(matrix, template_filename, pov_filename='out.pov', color=None, scale=2, norm=None):
    ''' generates povray code for a 3d image of the cube '''
    # load the template
    f = open(template_filename, 'r')
    output = f.read() + '\n'
    f.close()

    # generate all spheres
    X, Y, Z = matrix.shape

    # get ready to draw
    xs = 2. / (X - 1)
    ys = 2. / (Y - 1)
    zs = 2. / (Z - 1)
    maxvalue = np.amax(matrix)
    if norm == None:
        norm = .1 / maxvalue

    # choose colors
    if color != None:
        col = color

    for x in range(X):
        for y in range(Y):
            for z in range(Z):
                value = matrix[x, y, z]
                xx = x * xs - 1
                yy = y * ys - 1
                zz = z * zs - 1
                if color == None:
                    col = value / maxvalue
                if value > 0:
                    output += sphere(xx, yy, zz, value * norm * scale, col)

    # write the povray file
    f = open(pov_filename, 'w')
    f.write(output)
    f.close()
    render(pov_filename, scale)
