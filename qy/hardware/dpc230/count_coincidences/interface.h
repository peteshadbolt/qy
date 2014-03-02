// Write a triplet
void write_triplet(int a, int b, int c)
{
	if (counted_file==NULL){return;}
	int output_file_buffer[3];
	output_file_buffer[0]=a;
	output_file_buffer[1]=b;
	output_file_buffer[2]=c;
	fwrite(output_file_buffer, sizeof(int)*3, 1, counted_file);
}

// write all the other crap
void write_magic() {write_triplet(MAGIC, MAGIC, MAGIC);}
void write_scan_type(int n) {write_triplet(SCAN_TYPE, n, 0);}
void write_SCAN_NSTEPS(int n) {write_triplet(SCAN_NSTEPS, n, 0);}
void write_scan_nloops(int n) {write_triplet(SCAN_NLOOPS, n, 0);}
void write_scan_integration_time(int n) {write_triplet(SCAN_INTEGRATION_TIME, n, 0);}
void write_scan_close_shutter(int n) {write_triplet(SCAN_CLOSE_SHUTTER, n, 0);}
void write_scan_dont_move(int n) {write_triplet(SCAN_DONT_MOVE, n, 0);}
void write_scan_motor_controller(int which_mc) {write_triplet(SCAN_MOTOR_CONTROLLER, which_mc, 0);}
void write_scan_start_position(float position_mm) {write_triplet(SCAN_START_POSITION, (int)(position_mm*1e6), 0);}
void write_scan_stop_position(float position_mm) {write_triplet(SCAN_STOP_POSITION, (int)(position_mm*1e6), 0);}
void write_stop_metadata() {write_triplet(STOP_METADATA, 0, 0);}
void write_start_pause(int t) {write_triplet(START_PAUSE, t, 0);}
void write_stop_pause(int t) {write_triplet(STOP_PAUSE, t, 0);}
void write_motor_controller_update(int which_mc, float position_mm) {write_triplet(MOTOR_CONTROLLER_UPDATE, which_mc, (int)(position_mm*1e6));}
void write_scan_loop(int n) {write_triplet(SCAN_LOOP, n, 0);}
void write_scan_step(int n) {write_triplet(SCAN_STEP, n, 0);}
void write_start_count_rates(int n) {write_triplet(START_COUNT_RATES, n, 0);}
void write_count_rate(int pattern, int rate) {write_triplet(COUNT_RATE, pattern, rate);}
void write_stop_count_rates() {write_triplet(STOP_COUNT_RATES, 0, 0);}

void write_scan_label_nbytes(int n, char *s) {
	if (counted_file==NULL){return;}
	write_triplet(SCAN_LABEL_NBYTES, n, 0);
	fwrite(s, sizeof(char), n, counted_file);
}

void write_metadata(int type, int nsteps, int nloops, int integration_time, int close_shutter, 
					int dont_move, int motor_controller, float start_position, float stop_position, 
					int scan_label_nbytes, char *scan_label) {
	write_scan_type(type);
	write_SCAN_NSTEPS(nsteps);
	write_scan_nloops(nloops);
	write_scan_integration_time(integration_time);
	write_scan_close_shutter(close_shutter);
	write_scan_dont_move(dont_move);
	write_scan_motor_controller(motor_controller);
	write_scan_start_position(start_position);
	write_scan_stop_position(stop_position);
	write_scan_label_nbytes(scan_label_nbytes, scan_label);
	write_stop_metadata();
}

// Prepare for new data
void zero_rates()
{
	int i;
	fifo_gap=0;
	nonzero_pattern_count=0;
	for (i=0; i<65536; i+=1){pattern_rates[i]=0;}
}

// Nicer nomenclature
void start_integrating(){zero_rates();}

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

// Start a new COUNTED file
int new_counted_file(char* counted_filename)
{
	if (counted_file!=NULL){printf("Close the current COUNTED file before opening another!"); return -1;}
	counted_file=fopen(counted_filename, "wb");
	zero_rates();
	write_magic();
	printf("Started a new COUNTED file (%s) \n", counted_filename);
	file_open=1;
	return 1;
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

// Write the full set of nonzero patterns to disk
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
	
	// Perhaps, write to disk
	if (file_open && write_to_disk) {write_nonzero_patterns_to_disk();}
	
	// Finish
	return 1;
}
