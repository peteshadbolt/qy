// Delays across 16 channels, in timebins
int delays[16];

// Set the delays to some array
void set_delays(int *new_delays) 
{
    int i; 
    for (i=0; i<16; i+=1) {delays[i]=new_delays[i];}
    printf("Changed the delays\n");
}

// Just set the delays to zero
void zero_delays() 
{
    int i; 
    for (i=0; i<16; i+=1) {delays[i]=0;}
}

// Show the current delay settings
void show_delays() 
{
    printf("Delays:\n");
    int i; 
    for (i=0; i<16; i+=1) {printf("%d, ", delays[i]);}
    printf("\n");
}
