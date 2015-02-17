// Delays across 16 channels, in timebins
int delays[16];

char set_delays_tb_docs[] = "set_delays_tb(delays): Set the delay for each channel in TB";
static PyObject* set_delays_tb(PyObject* self, PyObject* args)
{ 
    PyObject *input;
    if (!PyArg_ParseTuple(args, "O!", &PyList_Type, &input)) { return NULL; }

    int i;
    int size=(int)PyList_Size(input);
    if (size>16){size=16;}
    int total=0;
    for (i = 0; i < size; i++) {
       int delay = (int)PyInt_AsLong(PyList_GetItem(input, (Py_ssize_t)i));
       delays[i]=delay;
       total += delay;    
    }
    
    PyObject *response = Py_BuildValue("i", total);
    return response;
}


// Just set the delays to zero
void zero_delays(void) 
{
    int i; 
    for (i=0; i<16; i+=1) {delays[i]=0;}
}


// Show the current delay settings
void show_delays(void) 
{
    printf("Delays:\n");
    int i; 
    for (i=0; i<16; i+=1) {printf("%d, ", delays[i]);}
    printf("\n");
}
