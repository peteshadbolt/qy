all: build

build: cross_correlate.c dpc.h
	python setup.py build_ext --inplace

test: build test.py
	python test.py

clean:
	rm -r build/
	rm cross_correlate.so

