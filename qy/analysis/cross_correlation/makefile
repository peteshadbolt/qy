all: build

build: cross_correlate.c delays.h
	python setup.py build_ext --inplace

test: build cross_correlate_test.py
	python cross_correlate_test.py

clean:
	rm -r build/
	rm cross_correlate.so

