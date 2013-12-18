from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import os
import sys 

# list all the packages
packages=[]
packages.append('qy')

# simulation packages
packages.append('qy.simulation')
for p in ['combinadics', 'linear_optics', 'bulk_optics', 'permanent', 'detection_model', 'qi']:
    packages.append('qy.simulation.'+p)

# other packages
packages.append('qy.analysis')
packages.append('qy.util')
packages.append('qy.graphics')
packages.append('qy.settings')
packages.append('qy.hardware')
packages.append('qy.hardware.counting')
packages.append('qy.hardware.heaters')
packages.append('qy.graphics')
packages.append('qy.wx')

# Cython extensions: fast permanennt and combinadics
extensions=[]
combi_path=os.path.join('simulation','combinadics', 'combi.pyx')
extensions.append(Extension('qy.simulation.combinadics.combi', [combi_path]))

perm_path=os.path.join('simulation','permanent', 'perm.pyx')
extensions.append(Extension('qy.simulation.permanent.perm', [perm_path]))

# SWIG extensions: dealing with the counting hardware. Should really convert these to cython
path=os.path.join('hardware', 'counting', 'counted_file', 'writer.i')
counted_file_writer=Extension('qy.hardware.counting.counted_file.writer', 
    [path], 
    swig_opts=['-modern', '-I../include']) 
extensions.append(counted_file_writer)

#parserc = os.path.join('hardware', 'counting', 'counted_file', 'counted_file_parser.c')
#parserwrapc = os.path.join('hardware', 'counting', 'counted_file' 'counted_file_parser_wrap.c')
#cf = Extension('qy.formats.counted_file._counted_file_parser', sources=[parserc, parserwrapc])
#extensions.append(cf)

# setup
setup(name='qy',
      version='1.0',
      package_dir={'qy': ''},
      packages=packages,
      cmdclass = {'build_ext': build_ext},
      ext_modules = extensions, 
      include_dirs = [numpy.get_include()])
      
