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
#include "coincidences.h"

// Prepare for new data
void zero_rates()
{
	int i;
	fifo_gap=0;
	nonzero_pattern_count=0;
	for (i=0; i<65536; i+=1){pattern_rates[i]=0;}
}

// Sets the coincidence window
void set_window(int new_window){
	window=new_window; 
	printf("Set the coincidence window to %d tb\n", window);
}

// Sets the time cutoff
void set_time_cutoff_ms(int new_time_cutoff_ms) {
	time_cutoff=new_time_cutoff_ms*1e12/TPB;
	printf("Set the time cutoff to %d ms\n", new_time_cutoff_ms);
}

// Close a COUNTED file
int close_counted_file()
{
	// Free memory
	free(nonzero_pattern_map);
	nonzero_pattern_map=NULL;
	
	// Close the file
	if (counted_file==NULL){printf("No file to close!\n"); return -1;}
	fclose(counted_file);
	counted_file=NULL;
	printf("Closed current COUNTED file.\n");
	file_open=0;
	return 1;
}

#include "pattern_defs.h"

// Process a particular integration step
int process_spc(char* spc_filename) {
	// Load the SPC file
	spc_file=fopen(spc_filename, "rb");
	if (spc_file==0){return -1;}
		
	// Pull all of the photons out of the file.
	int finished=0;
	grab_chunk();
	while (nrecords>0 && finished!=-1) {	
		finished=split_channels();
		count_coincidences();
		if (finished!=-1){grab_chunk();}
	}
	
	// Close the SPC file and write the data to disk
	fclose(spc_file);
	return 1;
}

// write the full set of nonzero patterns to disk
void write_nonzero_patterns_to_disk() {
	int i;
	write_start_count_rates(nonzero_pattern_count);
	for (i=0; i<nonzero_pattern_count; i+=1){
		int pattern=nonzero_pattern_map[i];
		write_count_rate(pattern, pattern_rates[pattern]);
	}
	write_stop_count_rates();
}

// Saves the data to disk and pulls out the count rates that we are interested in
int stop_integrating(int write_to_disk) {
	
	// Reallocate space for the nonzero rates
	int data_nbytes=sizeof(int)*3*(nonzero_pattern_count);
	if (nonzero_pattern_map==NULL) {
		nonzero_pattern_map=(int *)malloc(data_nbytes);
	} else {
		nonzero_pattern_map=(int *)realloc(nonzero_pattern_map, data_nbytes);
	}
	if ((nonzero_pattern_map==NULL) && (data_nbytes<0)){printf("Out of memory error!\n"); return -1;}
	
	// Pull out the nonzero data
	int pattern=1; int i=0;
	for (pattern=1; pattern<65536; pattern+=1) {
		if (pattern_rates[pattern]>0) {
			nonzero_pattern_map[i]=pattern;
			i+=1;
		}
	}
	
	// Finish
	return 1;
}

