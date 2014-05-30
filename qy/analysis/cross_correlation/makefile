all: build

build: cross_correlate.c dpc.h
	python setup.py build_ext --inplace

test: build test.py
	python test.py ~/physics/projects/test_data/minute.spc ab ad bc de -g -w 50

clean:
	rm -r build/
	rm cross_correlate.so
