// This python extension reads .SPC files from the Becker & Hickl DPC-230 timetagging card and computes cross-correlation functions.
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)
//

#include <stdio.h>
#include <stdlib.h>
#include <Python.h>
#include "dpc.h"
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
int start_channel;                      // ``start'' channel for cross-correlation
int stop_channel;                       // ``stop'' channel for cross-correlation
#define MAX_HISTOGRAM_BINS 1001 		// eighty feet ought to be enough for anyone
int histogram_bins;						// the size of the histogram
int histogram[MAX_HISTOGRAM_BINS];		// the histogram


// Implements the coincidence window
long long int quantize(long long int t, int win) {return t-(t % win);}


// Grabs a chunk of data from the SPC file
void grab_chunk(void){nrecords=fread(&buffer, 4, CHUNK_SIZE, spc_file);}


// Count bits in a string
int bitcount (int n)  {
   int count = 0 ;
   while (n)  {
      count++ ;
      n &= (n - 1) ;
   }
   return count ;
}


// Splits the current chunk of data into seperate buffers for the start and stop channels
int split_channels(void)
{
	int i;
	int this_record=0;				// this record
	int next_record=0;				// the previous record
	long long int high_time=0;		// stores the current high time
	
	channel_count[0]=0; channel_count[1]=0; 
	channel_index[0]=0; channel_index[1]=0; 
		

    printf("time cutoff %lld", time_cutoff);

	for (i=0; i < nrecords-1; i+=1)
	{
		this_record=buffer[i]; 
		next_record=buffer[i+1];
		
		if (is_photon(this_record))
		{

			photon_channel=photon_to_channel(this_record);
			
			photon_time=photon_to_time(this_record);
			photon_time=photon_time ^ high_time;
			if (photon_time>time_cutoff && time_cutoff>0){return -1;}
			
			if (photon_channel==start_channel) {channels[0][channel_count[0]]=photon_time; channel_count[0]+=1;}
			if (photon_channel==stop_channel) {channels[1][channel_count[1]]=photon_time; channel_count[1]+=1;}
		}
		
		if (is_high_time(next_record))
		{
			high_time=get_high_time(next_record);
			high_time=high_time << 24;
		}
	}
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


// Cross-correlates on the current chunk of data
int cross_correlate(void)
{
	int i=0; int j=0; int j0=0;
	long long int start_time;
	long long int stop_time;
	int bin;
	
	
	for (i=0; i<channel_count[0]; i+=1)
	{
		// find the first photon in the stop channel which is later than or equal to the photon in the start channel
		start_time=channels[0][i];
		j=j0;
		while (channels[1][j]<start_time){j+=1;}
		j0=j;
		bin=0;
		
		while (bin<histogram_bins && j<channel_count[1])
		{
			stop_time=channels[1][j];
			bin=stop_time-start_time;
			
			if (bin>=0 && bin<histogram_bins){histogram[bin]+=1;}
			j+=1;
		}
	}
	
	return 1;
}


// Builds the output histogram as a dictionary containing two lists
static PyObject* build_output_dict(void)
{

    PyObject *output_dict = PyDict_New();
    PyObject *key = Py_BuildValue("s", "awd");
    PyObject *value = Py_BuildValue("i", 1337);
    PyDict_SetItem(output_dict, key, value);
    return output_dict;
}


//*********************************************************
//Functions here provide an interface to the outside world


// The main cross-correlation process
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
        cross_correlate();
        if (finished!=-1){grab_chunk();}
    }
    
    // Close the SPC file 
    fclose(spc_file);

    // Prepare the data to return
    return build_output_dict();
}

static char set_histogram_bins_docs[] = "set_histogram_bins(n): Set the number of bins in the histogram";
static PyObject* set_histogram_bins(PyObject* self, PyObject* args)
{ 
    if (!PyArg_ParseTuple(args, "i", &histogram_bins)) { return NULL; }
    PyObject *response = Py_BuildValue("i", histogram_bins);
    return response;
}


static char set_channels_docs[] = "set_channels(start, stop): Set the START and STOP channels";
static PyObject* set_channels(PyObject* self, PyObject* args)
{ 
    if (!PyArg_ParseTuple(args, "ii", &start_channel, &stop_channel)) { return NULL; }
    PyObject *response = Py_BuildValue("i", 1);
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

static PyMethodDef cross_correlate_funcs[] = {
    {"set_histogram_bins", (PyCFunction)set_histogram_bins, METH_VARARGS, set_histogram_bins_docs},
    {"set_time_cutoff", (PyCFunction)set_time_cutoff, METH_VARARGS, set_time_cutoff_docs},
    {"set_channels", (PyCFunction)set_channels, METH_VARARGS, set_channels_docs},
    {"process_spc", (PyCFunction)process_spc, METH_VARARGS, process_spc_docs},
    {NULL}
};

void initcross_correlate(void)
{
    Py_InitModule3("cross_correlate", cross_correlate_funcs,
                   "Fast cross-correlation on timetags from the DPC-230");
}
