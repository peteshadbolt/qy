// This python extension parses .COUNTED FILES
// All questions to Peter Shadbolt (pete.shadbolt@gmail.com)

#include <stdio.h>
#include <stdlib.h>

// Global vars
FILE *counted_file;						// the SPC file
int triplet[3] = {0,0,0};				// the current triplet

int scan_label_nbytes=0;				// scan label nbytes
char scan_label[1000];					// the scan label
int temporary_file=0;
int scan_nsteps=0;
int scan_nloops=0;
int scan_integration_time=0;
int scan_close_shutter=0;
int scan_dont_move=0;
int scan_type=-1;
int scan_motor_controller=0;
int scan_start_position=0;
int scan_stop_position=0;

int motor_controller_positions[16] = {-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1};
int scan_step = 0;
int scan_loop = 0;
int paused = 0;
int aborted=1;

int pattern_rates[65536];
int nonzero_pattern_map[65536];
int nonzero_pattern_count=0;

// Include stuff
#include "counted_defs.h"
#include "pattern_defs.h"

// Clear the triplet
void clear_triplet() {
	triplet[0]=0;
	triplet[1]=0;
	triplet[2]=0;
}

// Read a triplet
int read_triplet() {	
	return fread(triplet, 12, 1, counted_file);   
}

// Open the counted file
int open_counted_file(char * fname) {
	counted_file=fopen(fname, "rb");
	if (counted_file==NULL){printf("Problem opening %s\n", fname); return -1;}
	//printf("Loaded %s\n", fname);
	return 1;
}

// Close the counted file
void close_counted_file() {
	if(counted_file==NULL){return;}
	fclose(counted_file);
	counted_file=NULL;
}

// Parse metadata
void read_metadata() {
	int n=1;
	triplet[0]=0; triplet[1]=0; triplet[2]=0;
	while ((n==1) && (triplet[0]!=STOP_METADATA))
	{
		n=read_triplet();
		if (triplet[0]==SCAN_LABEL_NBYTES) {
			scan_label_nbytes=triplet[1];
			fread(scan_label, scan_label_nbytes, 1, counted_file);
			scan_label[scan_label_nbytes+1]=0;
		}
		if (triplet[0]==TEMPORARY_FILE){temporary_file=triplet[1];}
		if (triplet[0]==SCAN_NSTEPS){scan_nsteps=triplet[1];}
		if (triplet[0]==SCAN_NLOOPS){scan_nloops=triplet[1];}
		if (triplet[0]==SCAN_INTEGRATION_TIME){scan_integration_time=triplet[1];}
		if (triplet[0]==SCAN_CLOSE_SHUTTER){scan_close_shutter=triplet[1];}
		if (triplet[0]==SCAN_DONT_MOVE){scan_dont_move=triplet[1];}
		if (triplet[0]==SCAN_TYPE){scan_type=triplet[1];}
		if (triplet[0]==SCAN_MOTOR_CONTROLLER){scan_motor_controller=triplet[1];}
		if (triplet[0]==SCAN_START_POSITION){scan_start_position=triplet[1];}
		if (triplet[0]==SCAN_STOP_POSITION){scan_stop_position=triplet[1];}
	}
}

// Read a chunk of data
int read_chunk() {
	int n=1; int p=0;
	int count_index=0;
	paused = 0;
	aborted = 1;
	n=read_triplet();
	
	while ((n==1) && (triplet[0]!=STOP_COUNT_RATES)) {
		//printf("%d\t%d\t%d\n", triplet[0], triplet[1], triplet[2]);
		if (n==1) {
			if (triplet[0]==MOTOR_CONTROLLER_UPDATE){motor_controller_positions[triplet[1]]=triplet[2];}
			if (triplet[0]==SCAN_STEP){scan_step=triplet[1];}
			if (triplet[0]==SCAN_LOOP){scan_loop=triplet[1];}
			if (triplet[0]==START_PAUSE){paused=1;}
			if (triplet[0]==START_COUNT_RATES){nonzero_pattern_count=triplet[1];}
			if (triplet[0]==COUNT_RATE){
				aborted=0;
				nonzero_pattern_map[count_index]=triplet[1];
				pattern_rates[triplet[1]]=triplet[2];
				count_index+=1;
			}
			p+=1;
		}
		n=read_triplet();
	}
	return p;
}

// interface
int get_paused() {return paused;}
int get_scan_step() {return scan_step;}
int get_scan_loop() {return scan_loop;}
float get_motor_controller_position(int index) { return motor_controller_positions[index]/((float)1e6); }

int get_aborted() {return aborted;}
int get_scan_label_nbytes() {return scan_label_nbytes;}
char * get_scan_label() {return (char *)scan_label;}
int get_temporary_file() {return temporary_file;}
int get_scan_nsteps() {return scan_nsteps;}
int get_scan_nloops() {return scan_nloops;}
int get_scan_integration_time() {return scan_integration_time;}
int get_scan_close_shutter() {return scan_close_shutter;}
int get_scan_dont_move() {return scan_dont_move;}
int get_scan_type() {return scan_type;}
int get_scan_motor_controller() {return scan_motor_controller;}
float get_scan_start_position() {return scan_start_position/((float) 1e6);}
float get_scan_stop_position() {return scan_stop_position/((float) 1e6);}
