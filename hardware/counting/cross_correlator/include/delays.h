int delays[16];				// delays across 16 channels, in timebins

// Reads delays from disk
void load_delays(char* fname)
{
	int q; 
	FILE *fd=fopen(fname, "r");	// the delay file
	if (fd==0){printf("Something is wrong with the delay file\n");};
	
	printf("Loaded delays: ");
	for (q=0; q<16; q+=1)
	{	
		int d;
		fscanf(fd, "%d\n", &d);
		delays[q]=d;
		printf("%d, ", delays[q]);
	}
	printf("\n");
	fclose(fd);
}

// Just set the delays to zero
void zero_delays()
{
	int q; 
	for (q=0; q<16; q+=1) {delays[q]=0;}
	printf("Delays are set to zero.\n");
}