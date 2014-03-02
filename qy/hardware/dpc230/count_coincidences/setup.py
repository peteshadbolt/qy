from setuptools import setup, find_packages, Extension
import os

extensions=[]
cc_path=os.path.join('count_coincidences.i')
cc_name='_count_coincidences'
count_coincidences = Extension(cc_name, [cc_path], swig_opts=['-I./'],  include_dirs=['/'])
extensions.append(count_coincidences)

setup(
    name = "count_coincidences",
    version = "0.1",
    packages = find_packages(),
    ext_modules=extensions,
    author = "Pete Shadbolt",
    author_email = "pete.shadbolt@gmail.com",
    description = "Fast coincidence counting",
    license = "MIT",
)
