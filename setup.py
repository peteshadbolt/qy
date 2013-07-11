from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import os

# list all the packages
packages=[]
packages.append('qy')

# simulation packages
packages.append('qy.simulation')
for p in ['combinadics', 'linear_optics', 'permanent', 'detection_model']:
    packages.append('qy.simulation.'+p)

# other packages
packages.append('qy.analysis')
packages.append('qy.io')
packages.append('qy.io.counted_file')
packages.append('qy.util')
packages.append('qy.graphics')
packages.append('qy.settings')
packages.append('qy.hardware')
packages.append('qy.wx')

# SWIG/cython extensions
extensions=[]
perm_path=os.path.join('simulation','permanent', 'perm.pyx')
extensions.append(Extension('qy.simulation.permanent.perm', [perm_path]))
parserc = os.path.join('io', 'counted_file', 'counted_file_parser.c')
parserwrapc = os.path.join('io', 'counted_file', 'counted_file_parser_wrap.c')
cf = Extension('qy.io.counted_file._counted_file_parser', sources=[parserc, parserwrapc])
extensions.append(cf)

# setup
setup(name='qy',
      version='1.0',
      package_dir={'qy': ''},
      packages=packages,
      cmdclass = {'build_ext': build_ext},
      ext_modules = extensions, 
      include_dirs = [numpy.get_include()])
      
