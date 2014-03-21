// This python extension reads .SPC files from the Becker & Hickl DPC-230 timetagging card and counts coincidences events
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <stdlib.h>
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
int window=30;                          // the coincidence window size
int nrecords=1;                         // the number of records we actually read from the disk
long fifo_gap=0;                        // tells us whether any data went missing due to a FIFO gap
long long int photon_time=0;            // the arrival time of this photon
int photon_channel=0;                   // the channel of the current photon
long long int time_cutoff;              // how many chunks we should process
int pattern_rates[65536];               // table of count rates


// Implements the coincidence window
long long int quantize(long long int t, int win) {return t-(t % win);}


// Grabs a chunk of data from the SPC file
void grab_chunk(){nrecords=fread(&buffer, 4, CHUNK_SIZE, spc_file);}


// Count bits in a string
int bitcount (int n)  {
   int count = 0 ;
   while (n)  {
      count++ ;
      n &= (n - 1) ;
   }
   return count ;
}


// Splits the current chunk of data into seperate buffers for each channel
int split_channels()
{
    int i;
    int this_record=0;              // this record
    int next_record=0;              // the previous record
    long long int high_time=0;      // stores the current high time
    
    // empty the channel counts and indeces
    for (i=0; i<16; i+=1){channel_count[i]=0; channel_index[i]=0;}
        
    // start building
    for (i=0; i < nrecords-1; i+=1)
    {
        this_record=buffer[i]; 
        next_record=buffer[i+1];
        
        if (is_photon(this_record))
        {
            if (has_gap(this_record)){fifo_gap+=1;}
            photon_channel=photon_to_channel(this_record);
            photon_time=photon_to_time(this_record);
            photon_time+=delays[photon_channel];
            photon_time=photon_time ^ high_time;
            if (photon_time>time_cutoff && time_cutoff>0) {
                /*printf("Bailed due to time cutoff");*/
                return -1;
            }
            channels[photon_channel][channel_count[photon_channel]]=photon_time;
            channel_count[photon_channel]+=1;
        }
        
        if (is_high_time(next_record)) 
        {
            high_time=get_high_time(next_record);
            high_time=high_time << 24;
        }
    }
    if (fifo_gap){printf("WARNING: FIFO gap. You are missing photons!");}
    return 0;
}


// Gets the next photon from the file
void get_next_photon()
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


// Counts coincidences in the current chunk of data
void count_coincidences()
{
    short pattern=0;                // Stores which coincidences we have
    long long int window_time=0;    // The quantized time of this window
    get_next_photon();
    while(photon_time!=-1)
    {
        photon_time=quantize(photon_time, window);
        if ((photon_time==window_time) ^ (photon_time==window_time+window))
        {
            // Update the picture of the event
            pattern = pattern ^ (1 << photon_channel);
        }
        else
        {
            // Store the event in the main table
            /*if ((pattern_rates[pattern]==0) && pattern!=0){nonzero_pattern_count+=1;}*/
            pattern_rates[pattern]+=1;
            // Get ready for the next event
            pattern = (1 << photon_channel);
        }
        window_time=photon_time;
        get_next_photon();
    }
}

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

// Builds the dictionary of count rates, to be returned to the user
static PyObject* build_output_dict()
{
    PyObject *output_dict = PyDict_New();
    int pattern=1; 
    int i=0;
    for (pattern=1; pattern<65536; pattern+=1) {
        if (pattern_rates[pattern]>0) {
            PyObject *key = label_from_binary_pattern(pattern);
            PyObject *value = Py_BuildValue("i", pattern_rates[pattern]);
            PyDict_SetItem(output_dict, key, value);
            i+=1;
        }
    }

    return output_dict;
}


// The main coincidence-counting process
static char process_spc_docs[] = "process_spc(filename): Process an SPC file";
static PyObject* process_spc(PyObject* self, PyObject* args)
{
    // Reset count rates, etc
    int i;
    fifo_gap=0;
    for (i=0; i<65536; i+=1){pattern_rates[i]=0;}

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
    
    // Close the SPC file 
    fclose(spc_file);

    // Prepare the data to return
    return build_output_dict();
}


static char set_window_docs[] = "set_window(window): Set the coincidence window TB";
static PyObject* set_window(PyObject* self, PyObject* args)
{ 
    if (!PyArg_ParseTuple(args, "i", &window)) { return NULL; }
    if (window<1){ window=1; }
    PyObject *response = Py_BuildValue("i", window);
    return response;
}

static char set_time_cutoff_docs[] = "set_time_cutoff(cutoff): Set the cutoff point in seconds";
static PyObject* set_time_cutoff(PyObject* self, PyObject* args)
{ 
    float new_time_cutoff;
    if (!PyArg_ParseTuple(args, "f", &new_time_cutoff)) { return NULL; }
    if (new_time_cutoff>.1) 
    { 
        time_cutoff=(long long)(new_time_cutoff*TPB_INV_SECS); 
    }
    PyObject *response = Py_BuildValue("L", time_cutoff);
    return response;
}


static PyMethodDef coincidence_funcs[] = {
    {"process_spc", (PyCFunction)process_spc, METH_VARARGS, process_spc_docs},
    {"set_window", (PyCFunction)set_window, METH_VARARGS, set_window_docs},
    {"set_time_cutoff", (PyCFunction)set_time_cutoff, METH_VARARGS, set_time_cutoff_docs},
    {"set_delays", (PyCFunction)set_delays, METH_VARARGS, set_delays_docs},
    {NULL}
};

void initcoincidence(void)
{
    Py_InitModule3("coincidence", coincidence_funcs,
                   "Fast coincidence counting for DPC230 timetag data. Unless otherwise stated, all units are in timebins (1 TB = 0.082 ns)");
}
