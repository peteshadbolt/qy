##qy

Quantum photonics with Python. 
Control and automation, DAQ, IO, simulation, graphics, GUI, analysis.

### Installing

This library is tested under [Python27](https://python.org/download/releases/2.7/). It depends on [numpy](http://numpy.org), [matplotlib](http://matplotlib.org).
For RS-232 communication with hardware, we need the [pySerial](http://pyserial.sourceforge.net/) library. For GUIs, we use [wx](http://wxpython.org).

Some old modules still depend on [Scipy](http://scipy.org) and [Cython](http://cython.org) --- soon these will no longer be required.  

To quickly get started with `qy` under Microsoft Windows, use the precompiled installer: TODO: implement this!

`qy` includes a number of optimized Python extensions written in `C`. If you want to modify and/or build from source, you will need a `C` compiler (I suggest [MinGW](http://www.mingw.org/) under Windows). A simple build/install is then done with
    
```bash
$ python setup.py build
$ python setup.py install
```    
    
You may need to tell `setuptools` which compiler to use

```bash
$ python setup.py build -c mingw32
$ python setup.py instal
```
    
If you are modifying code in `qy`, I strongly reccomend the `develop` mode provided by `setuptools`:

```bash
$ python setup.py develop
```

This saves typing `python setup.py install` before each test.

### Contents

- `qy.analysis` Statistical/data analysis. Coincidence counting, classical metrics, etc.
- `qy.formats` File formats. Currently just the `CTX` format, which attempts to provide a sane representation of laboratory data.
- `qy.graphics` Utility functions for graphing. Color pallettes. Some example code for generating 3D plots with [POVRay](http://povray.org).
- `qy.gui` `wx`-based user interface modules for various pieces of lab hardware. Focus on coincidence counting. 
- `qy.hardware` Interfaces to motor controllers, lasers, timetaggers, FPGAs, Arduinos, etc.
- `qy.settings` Keeps global settings for `qy` in a single place. Uses an `rc`-like format.
- `qy.simulation` Includes definitions for the circuit model (basis states, Paulis, 1-qubit/2-qubit gates), some bulk optical elements (HWP, QWP, polarizer etc).
- `qy.simulation.linear_optics` A generic `p`-photons-in-`m`-modes linear-optics simulator. Based around an optimized implementation of the permanent. Draws pretty pictures, and is quite fast for certain scenarios.
- `qy.util` Stuff with no other home. Timestamping, progress bars, unicode wrangling.

###TODO
- Optimize `settings` module (and standardize to `rc` format?).
- Get rid of Scipy (`$ grep -rl "scipy" ./`) 
- Stress test cython code in `linear_optics`
- Tidy up `hardware` modules, get code from other people e.g. PicoHarp
