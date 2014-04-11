##Qy for Python

Quantum photonics with Python. 
Control and automation, DAQ, IO, simulation, graphics, GUI, analysis.

### Dependencies

`qy` is tested under [Python27](https://python.org/download/releases/2.7/).

`qy` depends on [numpy](http://numpy.org), [matplotlib](http://matplotlib.org).
For RS-232 communication with hardware, we need the [pySerial](http://pyserial.sourceforge.net/) library. For GUIs, we use [wx](http://wxpython.org).

Some old modules still depend on [Scipy](http://scipy.org) and [Cython](http://cython.org) --- soon these will no longer be required.  


### Installing / testing / developing

To quickly get started with `qy` under Microsoft Windows, use the precompiled installer: TODO: implement this!

If you want to modify qy and/or build from source, you will need a `C` compiler (I suggest [MinGW](http://www.mingw.org/) under Windows). `qy` includes a number of Python extensions written in `C`. 

A simple build/install is then done with
    
    $ python setup.py build
    $ python setup.py install

### Contents

`qy` is broken into six sub-packages, for analysis, input/output, simulation of linear optics and quantum information, interfaces to various bits of lab hardware and DAQ, graphical user interfaces, and miscellaneous stuff.

####Analysis
Post-processing and analysis tools.
- Quantum metrics: quantum state fidelity, process fidelity, CHSH ...
- Classical metrics: Trace distance, statistical fidelity ...

####Formats
Non-standard file formats. In particular, a serial file format for long-running experiments.

####Simulation
Optimized code for simulating linear quantum optics and quantum information, some of which is written using [cython](http://cython.org).
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
