#!/usr/bin/env python

"""
setup.py file for counted_file_parser
"""

from distutils.core import setup, Extension

counted_file_parser_module = Extension('_counted_file_parser',
                           sources=['counted_file_parser_wrap.c', 'counted_file_parser.c'],
                           )

setup (name = 'counted_file_parser',
       version = '0.1',
       author      = "Pete Shadbolt pete.shadbolt@gmail.com",
       description = """Parse .COUNTED files""",
       ext_modules = [counted_file_parser_module],
       py_modules = ["counted_file_parser"],
       )