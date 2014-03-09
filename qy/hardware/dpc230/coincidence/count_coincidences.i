%module count_coincidences
/*%include <stdint.i>*/
/*%include "carrays.i"*/
/*%array_class(int, array);*/
/*%inline */

%{

extern int process_spc(char* spc_filename);

extern void set_delays(int* new_delays);
extern void set_window(int new_window);
extern void set_time_cutoff_ms(int new_time_cutoff_ms);

%}

extern int process_spc(char* spc_filename);

extern void set_delays(int* new_delays);
extern void set_window(int new_window);
extern void set_time_cutoff_ms(int new_time_cutoff_ms);
