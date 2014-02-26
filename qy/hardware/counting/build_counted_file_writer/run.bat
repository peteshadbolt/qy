@ echo off
cd %~dp0

echo ------------
echo SWIGGIN....
swig -python counted_file_writer.i

echo ------------
echo COMPILIN...
python setup.py build_ext --inplace -c mingw32

echo ------------
echo TESTIN....

python test.py

pause