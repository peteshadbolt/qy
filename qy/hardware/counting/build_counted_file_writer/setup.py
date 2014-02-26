#!/usr/bin/env python

"""
setup.py file for counted_file_writer
"""

from distutils.core import setup, Extension

counted_file_writer_module = Extension('_counted_file_writer',
                           sources=['counted_file_writer_wrap.c', 'counted_file_writer.c'],
                           )

setup (name = 'counted_file_writer',
       version = '0.1',
       author      = "Pete Shadbolt pete.shadbolt@gmail.com",
       description = """Count coincidences in DPC files and write them to a .COUNTED file""",
       ext_modules = [counted_file_writer_module],
       py_modules = ["counted_file_writer"],
       )