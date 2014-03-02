from setuptools import setup, find_packages, Extension
import os

extensions=[]
cc_path=os.path.join('qy', 'hardware', 'dpc230', 'count_coincidences', 'count_coincidences.i')
cc_name='qy.hardware.dpc230._count_coincidences'
count_coincidences = Extension(cc_name, [cc_path], swig_opts=['-modern', '-I../include'])
extensions.append(count_coincidences)

setup(
    name = "qy",
    version = "0.1",
    packages = find_packages(),
    ext_modules=extensions,
    test_suite='tests',
    author = "Pete Shadbolt",
    author_email = "pete.shadbolt@gmail.com",
    description = "Quantum photonics with python",
    license = "MIT",
    keywords = "quantum photonics",
    url = "https://github.com/peteshadbolt/qy/"   
)
