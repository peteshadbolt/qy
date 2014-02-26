// Implements the coincidence window
long long int quantize(long long int t, int win) {return t-(t % win);}

// Grabs a chunk of data from the SPC file
void grab_chunk(){nrecords=fread(&buffer, 4, CHUNK_SIZE, spc_file);}

// Splits the current chunk of data into seperate buffers for each channel
int split_channels()
{
	int i;
	int this_record=0;				// this record
	int next_record=0;				// the previous record
	long long int high_time=0;		// stores the current high time
	
	// empty the channel counts and indeces
	for (i=0; i<16; i+=1){channel_count[i]=0; channel_index[i]=0;}
		
	// start building
	for (i=0; i < nrecords-1; i+=1)
	{
		this_record=buffer[i]; 
		next_record=buffer[i+1];
		
		if (is_photon(this_record))
		{
			if (has_gap(this_record)){fifo_gap+=1;}
			photon_channel=photon_to_channel(this_record);
			photon_time=photon_to_time(this_record);
			photon_time+=delays[photon_channel];
			photon_time=photon_time ^ high_time;
			if (photon_time>time_cutoff && time_cutoff>0){/*printf("Bailed due to time cutoff.\n");*/ return -1;}
			channels[photon_channel][channel_count[photon_channel]]=photon_time;
			channel_count[photon_channel]+=1;
		}
		
		if (is_high_time(next_record)) 
		{
			high_time=get_high_time(next_record);
			high_time=high_time << 24;
		}
	}
	return 0;
}

// Gets the next photon from the file
void get_next_photon()
{
	int i;
	long long int t;
	photon_time=-1;
	photon_channel=-1;
	for (i=0; i<16; i++)
	{
		if (channel_index[i]<channel_count[i])
		{
			t=channels[i][channel_index[i]];
			if ((t<photon_time) ^ (photon_time==-1))
			{
				photon_time=t; photon_channel=i;
			}
		}
	}
	if (photon_time!=-1){channel_index[photon_channel]+=1;}
}

// Counts coincidences in the current chunk of data
void count_coincidences()
{
	int pattern=0;					// stores which coincidences we have
	long long int window_time=0;	// the quantized time of this window
	get_next_photon();
	while(photon_time!=-1)
	{
		photon_time=quantize(photon_time, window);
		if ((photon_time==window_time) ^ (photon_time==window_time+window))
		{
			pattern=pattern ^ (1 << photon_channel);
		}
		else
		{
			if ((pattern_rates[pattern]==0) && pattern!=0){nonzero_pattern_count+=1;}
			pattern_rates[pattern]+=1;
			pattern=(1 << photon_channel);
		}
		window_time=photon_time;
		get_next_photon();
	}
}