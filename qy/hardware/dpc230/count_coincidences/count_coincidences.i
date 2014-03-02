%module count_coincidences
%include <stdint.i>
%include "carrays.i"
%array_class(int, array);
%inline 

%{

extern int new_counted_file(char* counted_filename);
extern int close_counted_file();

extern void start_integrating();
extern int process_spc(char* spc_filename);
extern int stop_integrating(int write_to_disk);

extern int get_fpga_rate(int search_pattern);
extern int get_number_rate_8x2(int a, int b);
extern int get_number_rate_4x4(int a, int b, int c, int d);
extern int get_special_rate(int number);

extern void set_delays(int* new_delays);
extern void set_window(int new_window);
extern void set_time_cutoff_ms(int new_time_cutoff_ms);

extern void write_scan_type(int n);
extern void write_SCAN_NSTEPS(int n);
extern void write_scan_nloops(int n);
extern void write_scan_integration_time(int n);
extern void write_scan_close_shutter(int n);
extern void write_scan_dont_move(int n);
extern void write_scan_motor_controller(int which_mc);
extern void write_scan_start_position(float position_mm);
extern void write_scan_stop_position(float position_mm);
extern void write_scan_label_nbytes(int n, char *s);
extern void write_motor_controller_update(int which_mc, float position_mm);
extern void write_scan_loop(int n);
extern void write_scan_step(int n);
extern void write_stop_metadata();

extern void write_metadata(int type, int nsteps, int nloops, int integration_time, int close_shutter, 
					int dont_move, int motor_controller, float start_position, float stop_position, 
					int scan_label_nbytes, char *scan_label);


extern void write_start_pause(int t);
extern void write_stop_pause(int t);

%}
