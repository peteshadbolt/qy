void print_lld_binary(long long int x)
{
	int i;
	unsigned long long int q = 1;
	
	for (i=63; i>=0; i+=-1)
	{
		printf("%d", (x & (q << i))>0);
		if (i%4==0){printf(" ");}
	}
	printf("\n");
}

void print_d_binary(int x)
{
	int i;
	int q = 1;
	
	for (i=15; i>=0; i+=-1)
	{
		printf("%d", (x & (q << i))>0);
		if (i%4==0){printf(" ");}
	}
	printf("\n");
}