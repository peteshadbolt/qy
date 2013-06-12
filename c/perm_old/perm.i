%module perm

%{
    #define SWIG_FILE_WITH_INIT
    #include "perm.h"
%}

%include "numpy.i"

%init %{
    import_array();
%}


%apply (int* ARGOUT_ARRAY1, int DIM1) {(int* matrix, int n)}
%apply (int DIM1, int DIM2, double* INPLACE_ARRAY2 )
       {(unsigned int nrow, unsigned int ncol, double* mat)};

%include "perm.h"
