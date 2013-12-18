%module counted_file_parser
%include <stdint.i>
%include "carrays.i"
%array_class(int, array);
%inline 

%{
extern int open_counted_file(char * fname);
extern void close_counted_file();

extern void read_metadata();
extern int read_chunk();

extern int get_paused();
extern int get_scan_step();
extern int get_scan_loop();
extern float get_motor_controller_position(int index);

extern int get_scan_label_nbytes();
extern char * get_scan_label();
extern int get_temporary_file();
extern int get_scan_nsteps();
extern int get_scan_nloops();
extern int get_scan_integration_time();
extern int get_scan_close_shutter();
extern int get_scan_dont_move();
extern int get_scan_motor_controller();
extern float get_scan_start_position();
extern float get_scan_stop_position();
extern int get_scan_type();

extern int get_fpga_rate(int search_pattern);
extern int get_number_rate_8x2(int a, int b);
extern int get_number_rate_4x4(int a, int b, int c, int d);
extern int get_special_rate(int number);
extern int get_aborted();
%}
