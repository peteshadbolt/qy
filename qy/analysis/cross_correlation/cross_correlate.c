// This python extension reads .SPC files from the Becker & Hickl DPC-230 timetagging card and computes cross-correlation functions.
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)
//

#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include "dpc.h"

// Global vars
#define CHUNK_SIZE 200000
FILE *spc_file;                                 // the SPC file
int buffer[CHUNK_SIZE];                         // the photon buffer
long long int channels[2][CHUNK_SIZE];          // data, split up into channels
int channel_count[2];                           // last index used per channel
int channel_index[2];                           // last index used per channel
int nrecords=1;                                 // the number of records we actually read from the disk
long fifo_gap=0;                                // tells us whether any data went missing due to a FIFO gap
long long int photon_time=0;                    // the arrival time of this photon
int photon_channel=0;                           // the channel of the current photon
long long int integration_time;                 // how many chunks we should process
int start_channel;                              // ``start'' channel for cross-correlation
int stop_channel;                               // ``stop'' channel for cross-correlation
#define MAX_HISTOGRAM_BINS 1001 		        // eighty feet ought to be enough for anyone
int histogram_bins;						        // the size of the histogram
int *histogram;		                            // the histogram

// Grabs a chunk of data from the SPC file
void grab_chunk(void){nrecords=fread(&buffer, 4, CHUNK_SIZE, spc_file);}

// Splits the current chunk of data into seperate buffers for the start and stop channels
int split_channels(void)
{
	int i;
	int this_record=0;				// this record
	int next_record=0;				// the previous record
	long long int high_time=0;		// stores the current high time
	
	channel_count[0]=0; channel_count[1]=0; 
	channel_index[0]=0; channel_index[1]=0; 

	for (i=0; i < nrecords-1; i+=1) {
		this_record=buffer[i]; 
		next_record=buffer[i+1];
		
		if (is_photon(this_record)) {
			photon_channel=photon_to_channel(this_record);
			photon_time=photon_to_time(this_record) ^ high_time;
			if (photon_time>integration_time && integration_time>0){return -1;}
			if (photon_channel==start_channel) {channels[0][channel_count[0]]=photon_time; channel_count[0]+=1;}
			if (photon_channel==stop_channel) {channels[1][channel_count[1]]=photon_time; channel_count[1]+=1;}
		}
		
		if (is_high_time(next_record)) {
			high_time=get_high_time(next_record);
			high_time=high_time << 24;
		}
	}
	return 0;
}


// Cross-correlates on the current chunk of data
// Optionally flips start/stop channels, so that we can ``go back in time ''
int process_chunk(int flip)
{
	int i=0; int j=0; int j0=0;
	long long int start_time;
	long long int stop_time;
    int start = flip; int stop = !flip;
    int sign = 1-flip*2;
	int bin;
	for (i=0; i<channel_count[start]; i+=1)
	{
		// find the first photon in the stop channel which is later than or equal to the photon in the start channel
		start_time=channels[start][i];
		j=j0;
		while (channels[stop][j]<start_time){j+=1;}
		j0=j;
		bin=0;
		
		while (bin>=0 && bin<histogram_bins && j<channel_count[1])
		{
			stop_time=channels[stop][j];
            bin=sign*(stop_time-start_time)+histogram_bins/2;
			if (bin>=0 && bin<histogram_bins){histogram[bin]+=1;}
			j+=1;
		}
	}
	
	return 1;
}


// Build the output histogram as a dictionary containing two lists
static PyObject* build_output_dict(void)
{

    PyObject *output_dict = PyDict_New();
    PyObject *times = PyList_New(histogram_bins);
    PyObject *counts = PyList_New(histogram_bins);
    int i;
    for (i=0; i<histogram_bins; i+=1)
    {
        PyObject *time_entry = Py_BuildValue("f", 2*(i-histogram_bins/2)*TPB_NS);
        PyList_SetItem(times, i, time_entry);
        PyObject *count_entry = Py_BuildValue("i", histogram[i]);
        PyList_SetItem(counts, i, count_entry);

    }
    PyDict_SetItem(output_dict, Py_BuildValue("s", "times"), times);
    PyDict_SetItem(output_dict, Py_BuildValue("s", "counts"), counts);
    return output_dict;
}


//*********************************************************
//Functions here provide an interface to the outside world
//*********************************************************


// The main cross-correlation process
static char cross_correlate_docs[] = "cross_correlate(filename): Process an SPC file";
static PyObject* cross_correlate(PyObject* self, PyObject* args)
{
    // Parse the args
    const char* my_spc_filename;
    if (!PyArg_ParseTuple(args, "sii", &my_spc_filename, &start_channel, &stop_channel)) { return NULL; }
    printf("%s (START: %d / STOP: %d)\n", my_spc_filename, start_channel, stop_channel);

    // Reset count rates, etc
    int i;
    fifo_gap=0;
    histogram = malloc(sizeof(int)*histogram_bins);
    for (i=0; i<histogram_bins; i+=1){histogram[i]=0;}

    // Open the file
    spc_file=fopen(my_spc_filename, "rb");
    if (spc_file==0){return NULL;}
        
    // Examine all of the photons in the file.
    int finished=0;
    grab_chunk();
    while (nrecords>0 && finished!=-1) {    
        finished=split_channels();
        process_chunk(0);
        process_chunk(1);
        if (finished!=-1){grab_chunk();}
    }
    
    // Close the SPC file, prepare the data, free memory and return
    fclose(spc_file);
    PyObject* output = build_output_dict();
    free(histogram);
    return output;
}


static char set_histogram_width_docs[] = "set_histogram_width(n): Set the width of the histogram in ns";
static PyObject* set_histogram_width(PyObject* self, PyObject* args)
{ 
    float time_ns;
    if (!PyArg_ParseTuple(args, "f", &time_ns)) { return NULL; }
    printf("%f/%f=%f\n", time_ns, TPB_NS, time_ns/TPB_NS);

    /*histogram_bins = (int)(time_ns/TPB_NS);*/
    /*printf("Set histogram width to %.1f ns (%d bins)\n", time_ns, histogram_bins);*/
    PyObject *response = Py_BuildValue("i", histogram_bins);
    return response;
}


static char set_integration_time_docs[] = "set_integration_time(time): Set the cutoff point in seconds";
static PyObject* set_integration_time(PyObject* self, PyObject* args)
{ 
    float new_integration_time;
    if (!PyArg_ParseTuple(args, "f", &new_integration_time)) { return NULL; }
    if (new_integration_time>.1) { integration_time=(long long)(new_integration_time*TPB_INV_SECS); }
    printf("Set integration time to %.1f seconds\n", new_integration_time);
    PyObject *response = Py_BuildValue("L", integration_time);
    return response;
}


static PyMethodDef cross_correlate_funcs[] = {
    {"set_histogram_width", (PyCFunction)set_histogram_width, METH_VARARGS, set_histogram_width_docs},
    {"set_integration_time", (PyCFunction)set_integration_time, METH_VARARGS, set_integration_time_docs},
    {"cross_correlate", (PyCFunction)cross_correlate, METH_VARARGS, cross_correlate_docs},
    {NULL}
};


void initcross_correlate(void)
{
    Py_InitModule3("cross_correlate", cross_correlate_funcs,
                   "Fast cross-correlation on timetags from the DPC-230");
}
