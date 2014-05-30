// A map from becker and hickl's channel numbering scheme to ours. removes CFD inputs
short channel_map[21]={ -1, -1, -1,  0,  1,  2,  3,  4,  5,  6,  7, -1, -1,  8,  9, 10, 11, 12, 13, 14, 15};

// Time per bin
#define TPB_FS 82305.00030517578125
#define TPB_PS TPB_FS/1e3
#define TPB_NS TPB_FS/1e6
#define TPB_INV_SECS 1e15/TPB_FS

// Functions
int is_high_time(int p) {return p >> 30 == 1;}									// determines if this is a high time record
int is_photon(int p) {return p >> 30 == 0;}										// determines if this is a photon
int has_gap(int p) {return (p & (1<<29))>0;}									// determines if data was lost
int get_high_time(int p) {return p & 0x3fffffff;} 								// gets the high time value
int photon_to_time(int p) {return p & 16777215;} 								// extracts time from a photon record
short photon_to_channel(int p) {return channel_map[(p & 0x1f000000) >> 24];}	// extracts channel from a photon record
