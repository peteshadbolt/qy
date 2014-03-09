from distutils.core import setup, Extension
setup(name='coincidence', version='1.0',  \
      ext_modules=[Extension('coincidence', ['coincidence.c'])])
