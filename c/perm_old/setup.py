#! /usr/bin/env python

# System imports
from distutils.core import *
from distutils      import sysconfig

# Third-party modules - we depend on numpy for everything
import numpy

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# perm extension module
_perm = Extension("_perm",
                   ["perm.i" , "perm.c"],
                   include_dirs = [numpy_include],
                   )

# perm setup
setup(  name        = "permanent",
        description = "computes the permanent of an nxn complex matrix",
        author      = "pete shadbolt",
        version     = "1.0",
        ext_modules = [_perm]
        )
