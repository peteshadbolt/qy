Qy for Python
=============

Quantum libraries all in one place. Control and automation, DAQ, IO, simulation, graphics, GUI, analysis.

Analysis
-------
Post-processing and analysis tools.
- Quantum metrics: quantum state fidelity, process fidelity, CHSH ...
- Classical metrics: Trace distance, statistical fidelity ...

IO
--
Interface to non-standard binary formats.
- Fast interface to binary .COUNTED files from DPC-230

Simulation
----------
Optimized code for simulating linear quantum optics and quantum information, some of which is written using [cython](cython.org).
- Optimized linear optics simulator. *p* photons in *m* modes. Reck schemes, quantum walks, interferometers, random unitaries.
- Optimized permanent in cython.
- Optimized factorials and combinatorics
- Detection model for fan-out pseudo number-resolving detectors
- QI fundamentals: Qubit bases, Pauli operators, two-qubit gates...

Hardware
--------
Python drivers for various pieces of hardware.
- Motor controllers
- FPGA-based counting systems
- Lasers
- DAC (NI etc)
- ...

Util
----
- Easier file access, numpy tools, command line tools...
