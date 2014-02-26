// This python extension reads .SPC files from the Becker & Hickl DPC-230 timetagging card and counts coincidences events
// It then writes the data to a .COUNTED file
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <stdlib.h>

// Global vars
#define CHUNK_SIZE 2097152
FILE *spc_file;							// the SPC file
FILE *counted_file;						// the SPC file
int buffer[CHUNK_SIZE];					// the photon buffer
int pattern_rates[65536];				// counts pattern events
int nonzero_pattern_count=0;			// the number of nonzero count rates
int *nonzero_pattern_map=NULL;			// the variable length buffer of count rates that will be sent off to python
long long int channels[16][CHUNK_SIZE];	// data, split up into channels
int channel_count[16];					// last index used per channel
int channel_index[16];					// last index used per channel
int window=30;							// the coincidence window size
int nrecords=1;							// the number of records we actually read from the disk
long fifo_gap=0;						// tells us whether any data went missing due to a FIFO gap
long long int photon_time=0;			// the arrival time of this photon
int photon_channel=0;					// the channel of the current photon
long long int time_cutoff;				// how many chunks we should process
int file_open=0;						// avoids trying to write to disk when there is no file open

#include "counted_defs.h"
#include "dpc.h"
#include "delays.h"
#include "count_coincidences.h"
#include "interface.h"