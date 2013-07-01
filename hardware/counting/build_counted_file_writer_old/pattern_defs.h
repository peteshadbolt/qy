#define GET_A 0b0000000000001111
#define GET_B 0b0000000011110000
#define GET_C 0b0000111100000000
#define GET_D 0b1111000000000000

// Count bits in a number
int bitcount (int n)  {
   int count = 0 ;
   while (n)  {
      count++ ;
      n &= (n - 1) ;
   }
   return count ;
}

// Look up an FPGA-style pattern
int get_fpga_rate(int search_pattern) {
	int output_rate=0;
	int i; int pattern; int rate;
	// Iterate over all nonzero patterns
	for (i=0; i<nonzero_pattern_count; i+=1) {
		pattern=nonzero_pattern_map[i];
		rate=pattern_rates[pattern];
		if ((pattern & search_pattern) == search_pattern) {output_rate+=rate;}
	}
	return output_rate;
}

// Look up a number-resolved pattern
int get_number_rate(int a, int b, int c, int d) {
	int output_rate=0;
	int i; int pattern; int rate;
	int a_; int b_; int c_; int d_;
	// Iterate over all nonzero patterns
	for (i=0; i<nonzero_pattern_count; i+=1) {
		pattern=nonzero_pattern_map[i];
		rate=pattern_rates[pattern];
		a_=bitcount(GET_A & pattern);
		b_=bitcount(GET_B & pattern);
		c_=bitcount(GET_C & pattern);
		d_=bitcount(GET_D & pattern);
		if ((a_==a) && (b_==b) && (c_==c) && (d_==d)) {output_rate+=rate;}
	}
	return output_rate;
}

// Look up a special pattern
int get_special_rate(int number) {
	int output_rate=0;
	int i; int pattern; int rate;
	// Iterate over all nonzero patterns
	for (i=0; i<nonzero_pattern_count; i+=1) {
		pattern=nonzero_pattern_map[i];
		rate=pattern_rates[pattern];
		if (bitcount(pattern)>=number) {output_rate+=rate;}
	}
	return output_rate;
}