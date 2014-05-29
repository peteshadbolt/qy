from setuptools import setup, Extension
from glob import glob
import numpy as np
print np.get_include()

setup(name = 'permanent', 
      version = '1.0',  
      ext_modules = [Extension('permanent', ['permanent.c'])],
      include_dirs = [np.get_include()+'/numpy']
      )
