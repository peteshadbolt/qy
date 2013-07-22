Qy for Python
-------------

Quantum libraries all in one place. Control and automation, DAQ, IO, simulation, graphics, GUI, analysis. [Installation instructions](#installing)

###Installing 

qy depends on [numpy](http://numpy.org) and [matplotlib](http://matplotlib.org). I am trying to avoid dependency on [SciPy](http://scipy.org), but some functions (`$ grep -rl "scipy" ./`) still need it. You will need [cython](http://cython.org) and [SWIG](http://swig.org) if you want to compile from source.



will root out files which have leftover Scipy dependencies.

####Windows
I am periodically building windows installers. You can download them [here](https://github.com/peteshadbolt/qy/tree/master/dist).
Under windows using [mingw32](http://www.mingw.org/), the following commands seem to do the job when building from source:

    > python setup.py build --compiler mingw32
    > python setup.py install

####Linux
Under linux, this is the command that I am using to compile/build and install qy:

    $ python setup.py  install --user

The --user is optional.

## Contents

###Analysis
Post-processing and analysis tools.
- Quantum metrics: quantum state fidelity, process fidelity, CHSH ...
- Classical metrics: Trace distance, statistical fidelity ...

###IO
Interface to non-standard binary formats.
- Fast interface to binary .COUNTED files from DPC-230

###Simulation
Optimized code for simulating linear quantum optics and quantum information, some of which is written using [cython](http://www.cython.org).
- Optimized linear optics simulator. *p* photons in *m* modes. Reck schemes, quantum walks, interferometers, random unitaries.
- Optimized permanent in cython.
- Optimized factorials and combinatorics
- Detection model for fan-out pseudo number-resolving detectors
- QI fundamentals: Qubit bases, Pauli operators, two-qubit gates...

###Hardware
Python drivers for various pieces of hardware.
- Motor controllers
- FPGA-based counting systems
- Lasers
- DAC (NI etc)
- ...

###GUI
Useful wrappers for various bits of [wxPython](http://wxpython.org).

###Miscellaneous useful things
- Easier file access, numpy tools, command line tools...

