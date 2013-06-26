from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

# list all the packages
packages=[]
packages.append('qy')

packages.append('qy.simulation')
for p in ['combinadics', 'linear_optics', 'permanent', 'detection_model']:
    packages.append('qy.simulation.'+p)

packages.append('qy.analysis')
packages.append('qy.io')
packages.append('qy.io.counted_file')
packages.append('qy.util')


extensions=[]
extensions.append(Extension('qy.simulation.permanent.perm', ['./simulation/permanent/perm.pyx']))
cf = Extension('qy.io.counted_file._counted_file_parser', sources=['./io/counted_file/counted_file_parser.c','./io/counted_file/counted_file_parser_wrap.c'],)
extensions.append(cf)


setup(name='qy',
      version='1.0',
      package_dir={'qy': ''},
      packages=packages,
      cmdclass = {'build_ext': build_ext},
      ext_modules = extensions, 
      include_dirs = [numpy.get_include()])
      
