// This python extension provides fast methods to calculate the permanent
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <Python.h>
#include "arrayobject.h"

// Global vars

// TODO: Example interface
static char permanent_docs[] = "permanent(M): Returns the permanent of a Numpy matrix M";
static PyObject* permanent(PyObject* self, PyObject* args)
{
    // Pull in the matrix
    const char* my_spc_filename;
    if (!PyArg_ParseTuple(args, "s", &my_spc_filename)){ return NULL; }
    
    // Prepare the data to return
    PyObject *response = Py_BuildValue("i", 1337);
    return response;
}


static PyMethodDef permanent_funcs[] = {
    {"permanent", (PyCFunction)permanent, METH_VARARGS, permanent_docs},
    {NULL}
};

void initpermanent(void)
{
    Py_InitModule3("permanent", permanent_funcs,
                   "Calculate permanents as fast as possible.");
}
