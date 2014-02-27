##Qy for Python

Quantum photonics with Python. Control and automation, DAQ, IO, simulation, graphics, GUI, analysis.

### Installing

I recently moved from disutils to setuptools. I'm sure this will create headaches...

### Contents

`qy` is broken into six sub-packages, for analysis, input/output, simulation of linear optics and quantum information, interfaces to various bits of lab hardware and DAQ, graphical user interfaces, and miscellaneous stuff.

####Analysis
Post-processing and analysis tools.
- Quantum metrics: quantum state fidelity, process fidelity, CHSH ...
- Classical metrics: Trace distance, statistical fidelity ...

####Formats
Non-standard file formats. In particular, a serial file format for long-running experiments.

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
