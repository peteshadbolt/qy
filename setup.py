from distutils.core import setup
packages=[]
packages.append('qy')

packages.append('qy.simulation')
for p in ['combinadics', 'linear_optics', 'permanent', 'detection_model']:
    packages.append('qy.simulation.'+p)

packages.append('qy.analysis')
packages.append('qy.io')
packages.append('qy.io.counted_file')

setup(name='qy',
      version='1.0',
      package_dir={'qy': ''},
      packages=packages
      )
