// Post-processes SPC data files, emulating a picoharp
// version 0.1
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include "spc.h"
#define chunk_size 2097152		// how much data we read at once. make sure this many 4-byte records fit in memory!
#define bin_count 100			// how many time bins we have (300)

// Global vars
FILE *fp;						// the SPC file
int buffer[chunk_size];			// the photon buffer
int histogram_bins[bin_count];	// the photon buffer
int tpb;						// the time per bin, in femtoseconds
int nrecords=1;					// the number of records we actually read from the disk
int start_channel;				// the start channel
int stop_channel;				// the stop channel
long long int time_cutoff;		// how many chunks we should proces

// Grab a chunk of data from the file
void spc_grab_chunk()
{
	nrecords=fread(&buffer, 4, chunk_size, fp);
	float mb=(nrecords*4.)/1048576.;
	printf("%.2f MB read from disk\n", mb);
}

// Saves the data in a reasonably efficient, readable way
void save_data(char* fname)
{
	// get the new filename
	char ext[] = ".histogram";
	strcat(fname, ext);
		
	int q;
	fp = fopen(fname,"w"); fprintf(fp, ""); fclose(fp);
	fp = fopen(fname,"a+");
	for (q=1; q<bin_count; q+=1)
	{
		fprintf(fp, "%d\n", histogram_bins[q]);
	}
	fclose(fp);
	printf("Wrote data to %s\n", fname);
}

// Main analysis loop
int analyze_chunk()
{
	int i; int j; short finished;
	int start_record=0;						// the start record
	int stop_record=0;						// the stop record
	long long int start_time=0;				// the arrival time of the start photon
	long long int stop_time=0;				// the arrival time of the stop photon
	long long int high_time=0;				// stores the current high time
	long long int bin;
				
	// search over all photons
	for (i=0; i < nrecords-1; i+=1)
	{
		start_record=buffer[i];
		if (is_photon(start_record) && photon_to_channel(start_record)==start_channel)
		{
			start_time=photon_to_time(start_record) ^ high_time;
			if(start_time>time_cutoff){return -1;}	// check to see if we have exceeded the time cutoff
			j=i;
			finished=0;
			while ((j < nrecords-1) && !finished)
			{
				stop_record=buffer[j];
				if (is_photon(stop_record) && photon_to_channel(stop_record)==stop_channel)
				{
						stop_time=photon_to_time(stop_record) ^ high_time;
						bin=stop_time-start_time;
						if (bin>=bin_count) {finished=1;}
						if ((bin<bin_count) && (bin>0)) {histogram_bins[bin]+=1;}
				}
				j+=1;
			}
		}
		
		if (is_high_time(buffer[i+1])) 
		{
			high_time=get_high_time(buffer[i+1]);
			high_time=high_time << 24;
		}
		
	}
}

// *********** Main ***********
int main(int argc, char *argv[])
{
	// Check that we have been given some data to process
	if (argc>5 || argc<4) {printf( "usage: %s [spc file] [startc] [stopc] [[tc]]\n", argv[0] ); return 0;}
	fp=fopen(argv[1], "rb");
	start_channel=atoi(argv[2]);
	stop_channel=atoi(argv[3]);
	printf("Start: %d\tStop: %d\n", start_channel, stop_channel);
				
	// Load data, check that the descriptor makes sense, grab a chunk
	tpb=check_descriptor(fp);
	printf("Timing resolution : %.5f ns\n", (tpb/1e6));
	
	// Figure out the time cutoff
	if (argc==5) {time_cutoff=atoi(argv[4]);} else {time_cutoff=1;}
	printf("Time cutoff : %llds\n", time_cutoff);
	time_cutoff=time_cutoff*1e15/tpb;
	time_cutoff=time_cutoff/10;
	
	// Get a starter chunk
	spc_grab_chunk();
	
	int ret=1;
	// Analyze all the data
	while (nrecords>0 && ret!=-1)
	{	
		ret=analyze_chunk();
		if (ret!=-1){spc_grab_chunk();}
	}
	
	// Close the SPC file, finish the job
	fclose(fp);
	save_data(argv[1]);
}