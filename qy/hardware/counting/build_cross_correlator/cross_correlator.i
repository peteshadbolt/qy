%module cross_correlate
%include <stdint.i>
%include "carrays.i"
%array_class(int, array);
%inline 

%{
extern int open_counted_file(char * fname);
extern void close_counted_file();

extern void read_metadata();
extern int read_chunk();

%}