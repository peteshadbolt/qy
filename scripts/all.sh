#!/bin/bash
rm -r ./build
python scripts/pep8.py
python setup.py build > build.log
grep -R TODO > todo.mkd
nosetests > nose.log
