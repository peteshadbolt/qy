from distutils.core import setup, Extension
from glob import glob
setup(name='cross_correlate', version='1.0',  \
      ext_modules=[Extension('cross_correlate', ['cross_correlate.c'])]
      )
