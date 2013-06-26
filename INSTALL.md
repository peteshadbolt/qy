
Installing qy
=============

This is still a work-in-progress.

Firstly, qy depends on a number of libraries, most notably Numpy and Matplotlib.

I am trying to remove dependency on Scipy.

Under linux, this is the command that I am using to compile/build and install qy:

    $ python setup.py  install --user

Under windows, the first thing to do is copy the contents into C:/Python27/Lib/site-packages/qy

Next, you need to figure out how to compile the Cython and SWIG C-based extensions. Good luck, expect pain!
