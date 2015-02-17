all: test

coincidence.so: src/*
	python setup.py build_ext --inplace

test: coincidence.so
	python test.py

clean:
	@rm -f coincidence.so
