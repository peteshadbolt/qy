##Qy for Python

Quantum libraries all in one place. Control and automation, DAQ, IO, simulation, graphics, GUI, analysis.

###Installing 

`qy` depends on [numpy](http://numpy.org) and [matplotlib](http://matplotlib.org). I am trying to avoid dependency on [SciPy](http://scipy.org), but some functions still need it. You will need [cython](http://cython.org) and [SWIG](http://swig.org) if you want to compile from source.

####Windows
I am periodically building windows installers. You can download them [here](https://github.com/peteshadbolt/qy/tree/master/dist).
Under windows using [mingw32](http://www.mingw.org/), the following commands seem to do the job when building from source:

    > python setup.py build --compiler mingw32
    > python setup.py install

####Linux
Under linux, this is the command that I am using to compile/build and install qy:

    $ python setup.py  install --user

The `--user` is optional.

### Contents

`qy` is broken into six sub-packages, for analysis, input/output, simulation of linear optics and quantum information, interfaces to various bits of lab hardware and DAQ, graphical user interfaces, and miscellaneous stuff.

####Analysis
Post-processing and analysis tools.
- Quantum metrics: quantum state fidelity, process fidelity, CHSH ...
- Classical metrics: Trace distance, statistical fidelity ...

####IO
Interface to non-standard binary formats.
- Fast interface to binary `.counted` files from [DPC-230](http://www.becker-hickl.com/pdf/dbdpc3.pdf) timetagger

####Simulation
Optimized code for simulating linear quantum optics and quantum information, some of which is written using [cython](http://www.cython.org).
- Optimized linear optics simulator. *p* photons in *m* modes. Reck schemes, quantum walks, interferometers, random unitaries.
- Optimized permanent in cython.
- Optimized factorials and combinatorics
- Detection model for fan-out pseudo number-resolving detectors
- QI fundamentals: Qubit bases, Pauli operators, two-qubit gates...

####Hardware
Python drivers for various pieces of hardware.
- Motor controllers
- FPGA-based counting systems
- Lasers
- DAC (NI etc)
- ...

####GUI
Useful wrappers for various bits of [wxPython](http://wxpython.org).

####Miscellaneous useful things
- Easier file access, numpy tools, command line tools...

###TODO
- Get rid of Scipy (`$ grep -rl "scipy" ./`) 
- Stress test cython code in `linear_optics`
- Tidy up `hardware` modules, get code from other people e.g. PicoHarp
