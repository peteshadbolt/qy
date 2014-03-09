from setuptools import setup, find_packages, Extension
import os
from glob import glob

#paths=['count_coincidences.i']+glob('*.c')
paths=['count_coincidences.c', 'count_coincidences_wrap.c']
swig_opts=[]
count_coincidences = Extension('_count_coincidences', sources=paths, swig_opts=swig_opts)

setup(
    name = "count_coincidences",
    version = "0.1",
    packages = find_packages(),
    ext_modules=[count_coincidences],
    py_modules=['example'],
    author = "Pete Shadbolt",
    author_email = "pete.shadbolt@gmail.com",
    description = "Fast coincidence counting",
    license = "MIT",
)
