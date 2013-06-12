@echo off
echo SWIG
swig -python perm.i

echo COMPILE
python setup.py build_ext --inplace -c mingw32

python test_perm.py

