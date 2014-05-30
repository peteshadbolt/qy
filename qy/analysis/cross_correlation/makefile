all: build

build: cross_correlate.c dpc.h
	python setup.py build_ext --inplace

test: build xc.py
	python xc.py ~/physics/projects/test_data/minute.spc ab

clean:
	rm -r build/
	rm cross_correlate.so

