from setuptools import setup, find_packages, Extension
import os


# Fast coincidence-counting code
path=os.path.join('qy', 'analysis', 'coincidence', 'coincidence.c')
coincidence = Extension('qy.analysis.coincidence', [path])

extensions = [coincidence]

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
