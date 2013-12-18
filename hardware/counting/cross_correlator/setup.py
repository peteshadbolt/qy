#!/usr/bin/env python

"""
setup.py file for cross_correlate
"""

from distutils.core import setup, Extension

cross_correlate_module= Extension('_cross_correlate',
                           sources=['cross_correlate_wrap.c', 'cross_correlate.c'],
                           )

setup (name = 'cross_correlate',
       version = '0.1',
       author      = "Pete Shadbolt pete.shadbolt@gmail.com",
       description = """Get cross correlation curves from SPC files""",
       ext_modules = [cross_correlate_module],
       py_modules = ["cross_correlate"],
       )