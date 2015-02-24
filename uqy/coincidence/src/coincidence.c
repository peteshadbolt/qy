// This python extension reads .SPC files from the Becker & Hickl DPC-230 timetagging card and counts coincidences events
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <Python.h>
#include "dpc.h"
#include "delays.h"
char ALPHABET[16] = "abcdefghijklmnop";

// Global vars
#define CHUNK_SIZE 200000
FILE *spc_file;                         // the SPC file
int buffer[CHUNK_SIZE];                 // the photon buffer
long long int channels[16][CHUNK_SIZE]; // data, split up into channels
int channel_count[16];                  // last index used per channel
int channel_index[16];                  // last index used per channel
int coincidence_window=30;              // the coincidence window size
int nrecords=1;                         // the number of records we actually read from the disk
long fifo_gap=0;                        // tells us whether any data went missing due to a FIFO gap
long long int photon_time=0;            // the arrival time of this photon
long long int slice_time=0;             // the beginning of the slice
long int slice_window=30;               // timing slice window
int photon_channel=0;                   // the channel of the current photon
long long int time_cutoff;              // how many chunks we should process
int pattern_rates[65536];               // table of count rates
long long int high_time=0;              // stores the current high time
PyObject *output_times;                 // where we put the final dataset
PyObject *output_counts;                // where we put the final dataset

// Implements the coincidence window
long long int quantize(long long int t, int win) {return t==-1 ? -1 : t-(t % win);}


// Grabs a chunk of data from the SPC file
void grab_chunk(void){nrecords=fread(&buffer, 4, CHUNK_SIZE, spc_file);}


// Takes a pattern represented in binary (i.e. an int). 
// e.g. 0000000000011000 = 2^3+2^4 = 8+16 = 24 = "LM"
static PyObject* label_from_binary_pattern(int pattern)
{
    char label[17];
    int i=0;
    int j=0;
    for (i=0; i<16; i+=1) {
        if ((pattern & 1<<i) > 0) {
            label[j]=ALPHABET[i];
            j+=1;
        }
    }
    PyObject *response = Py_BuildValue("s#", label, j);
    return response;
}


// Builds the dictionary of count rates, to be returned to python
static PyObject* build_counts_dict(void)
{
    PyObject *counts_dict = PyDict_New();
    int pattern=1; 
    int i=0;
    for (pattern=1; pattern<65536; pattern+=1) {
        if (pattern_rates[pattern]>0) {
            PyObject *key = label_from_binary_pattern(pattern);
            PyObject *value = Py_BuildValue("i", pattern_rates[pattern]);
            PyDict_SetItem(counts_dict, key, value);
            i+=1;
        }
    }
    return counts_dict;
}

// Splits the current chunk of data into seperate buffers for each channel
// The main task here is to sort photons into a single serial array
int split_channels(void)
{
    int i;
    int this_record=0;              // this record
    
    // empty the channel counts and indeces
    for (i=0; i<16; i+=1){channel_count[i]=0; channel_index[i]=0;}
        
    // start building
    for (i=0; i < nrecords-1; i+=1)
    {
        this_record=buffer[i]; 
        if (is_photon(this_record))
        {
            if (has_gap(this_record)){fifo_gap+=1;}
            photon_channel = photon_to_channel(this_record);
            photon_time = (photon_to_time(this_record) + delays[photon_channel]) ^ high_time; 
            if (photon_time>time_cutoff && time_cutoff>0) {
                printf("bailed %f\n", photon_time*TPB/1e15);
                return -1;
            }
            channels[photon_channel][channel_count[photon_channel]]=photon_time;
            channel_count[photon_channel]+=1;
        } 
        else if (is_high_time(this_record)) 
        {
            high_time=get_high_time(this_record);
            high_time=high_time << 24;
        }
    }
    if (fifo_gap > 0){printf("WARNING: FIFO gap. You are missing photons!");}
    return 0;
}


// Gets the next photon from the file
void get_next_photon(void)
{
    int i;
    long long int t;
    photon_time=-1;
    photon_channel=-1;
    for (i=0; i<16; i++)
    {
        if (channel_index[i]<channel_count[i])
        {
            t=channels[i][channel_index[i]];
            if ((t<photon_time) ^ (photon_time==-1))
            {
                photon_time=t; photon_channel=i;
            }
        }
    }
    if (photon_time!=-1){channel_index[photon_channel]+=1;}
}

// Finish a slice - generates a dictionary 
void finish_slice(void){
    int i;
    PyObject *key = Py_BuildValue("i", (int)round(TPB*slice_time/1e12));
    PyObject *value = build_counts_dict();
    PyList_Append(output_times, key);
    PyList_Append(output_counts, value);
    for (i=0; i<65536; i+=1){pattern_rates[i]=0;}
}


// Counts coincidences in the current chunk of data
void count_coincidences(void)
{
    int pattern=0;                  // Stores which coincidences we have
    long long int window_time=0;    // The quantized time of this window
    while(photon_time!=-1)
    {
        get_next_photon();
        photon_time=quantize(photon_time, coincidence_window);
        if (photon_time==window_time)
        {
            pattern = pattern ^ (1 << photon_channel); // Update the picture of the event
        }
        else
        {
            window_time=photon_time;
            // Store the event in the main table
            pattern_rates[pattern]+=1;
            // Get ready for the next event
            pattern = (1 << photon_channel);
            // Did we reach the end of a slice? If so, put the current data in a dictionary and reset the table of count rates
            if (photon_time > slice_time + slice_window)
            {
                while (photon_time > slice_time + slice_window){
                    finish_slice();
                    slice_time+=slice_window;
                }
            }
        }

    }
    /*finish_slice();*/
}

// The main coincidence-counting process
static char process_spc_docs[] = "process_spc(filename): Process an SPC file";
static PyObject* process_spc(PyObject* self, PyObject* args)
{
    // Reset count rates, etc
    int i;
    fifo_gap=0;
    high_time=0;
    slice_time=0;
    for (i=0; i<65536; i+=1){pattern_rates[i]=0;}
    slice_time = 0;
    output_counts = PyList_New(0);
    output_times = PyList_New(0);

    // Load the SPC file
    const char* my_spc_filename;
    if (!PyArg_ParseTuple(args, "s", &my_spc_filename)){ return NULL; }
    spc_file=fopen(my_spc_filename, "rb");
    if (spc_file==0){return NULL;}
        
    // Examine all of the photons in the file.
    int finished=0;
    grab_chunk();
    while (nrecords>0 && finished!=-1) {    
        finished=split_channels();
        count_coincidences();
        if (finished!=-1){grab_chunk();}
    }
    finish_slice();
    
    // Close the SPC file 
    fclose(spc_file);

    // Prepare the data to return
    PyObject *output_dict = PyDict_New();
    PyDict_SetItem(output_dict, Py_BuildValue("s", "times"), output_times);
    PyDict_SetItem(output_dict, Py_BuildValue("s", "slices"), output_counts);
    return output_dict;
}


static char set_coincidence_window_tb_docs[] = "set_coincidence_window_tb(coincidence_window): Set the coincidence window TB";
static PyObject* set_coincidence_window_tb(PyObject* self, PyObject* args)
{ 
    if (!PyArg_ParseTuple(args, "i", &coincidence_window)) { return NULL; }
    if (coincidence_window<1){ coincidence_window=1; }
    PyObject *response = Py_BuildValue("i", coincidence_window);
    printf("Set coincidence window to %d tb (%.1f ns)\n", coincidence_window, coincidence_window * TPB/1e6);
    return response;
}

static char set_slice_window_ms_docs[] = "set_slice_window_ms(slice_window): Set the timing slice window";
static PyObject* set_slice_window_ms(PyObject* self, PyObject* args)
{ 
    float new_slice_window_ms;
    if (!PyArg_ParseTuple(args, "f", &new_slice_window_ms)) { return NULL; }
    slice_window = (long long)(new_slice_window_ms * TPB_INV_MS);
    if (slice_window<1){ slice_window=1; }
    PyObject *response = Py_BuildValue("i", slice_window);
    return response;
}

static char set_time_cutoff_s_docs[] = "set_time_cutoff_s(cutoff): Set the cutoff point in seconds";
static PyObject* set_time_cutoff_s(PyObject* self, PyObject* args)
{ 
    float new_time_cutoff_s;
    if (!PyArg_ParseTuple(args, "f", &new_time_cutoff_s)) { return NULL; }
    if (new_time_cutoff_s>.1) { time_cutoff=(long long)(new_time_cutoff_s*TPB_INV_SECS); }
    PyObject *response = Py_BuildValue("L", time_cutoff);
    return response;
}


static char wtf_docs[] = "wtf(): WTF is about to happen ... ?";
static PyObject* wtf(PyObject* self, PyObject* args)
{ 
    printf("Coincidence counting setup:\n");
    float cutoff_s = time_cutoff*TPB/1e15;
    float slice_window_ms = (float)slice_window * TPB/1e12;
    float coincidence_window_ns = coincidence_window * TPB/1e6;
    int n_slices = (int)(1000*cutoff_s / slice_window_ms);
    printf("  I'm going to consume at most %.1f s of data.\n", cutoff_s);
    printf("  I'll slice it up into %d x %.1f ms slices.\n", n_slices, slice_window_ms);
    printf("  For each slice, I'll count all coincidences with a window of %.1f ns.\n", coincidence_window_ns);
    PyObject *response = Py_BuildValue("i", 0);
    return response;
}


static PyMethodDef coincidence_funcs[] = {
    {"process_spc", (PyCFunction)process_spc, METH_VARARGS, process_spc_docs},
    {"set_coincidence_window_tb", (PyCFunction)set_coincidence_window_tb, METH_VARARGS, set_coincidence_window_tb_docs},
    {"set_slice_window_ms", (PyCFunction)set_slice_window_ms, METH_VARARGS, set_slice_window_ms_docs},
    {"set_time_cutoff_s", (PyCFunction)set_time_cutoff_s, METH_VARARGS, set_time_cutoff_s_docs},
    {"set_delays_tb", (PyCFunction)set_delays_tb, METH_VARARGS, set_delays_tb_docs},
    {"wtf", (PyCFunction)wtf, METH_VARARGS, wtf_docs},
    {NULL}
};

void initcoincidence(void)
{
    Py_InitModule3("coincidence", coincidence_funcs,
                   "Fast coincidence counting for DPC230 timetag data. Unless otherwise stated, all units are in timebins (1 TB = 0.082 ns)");
}
