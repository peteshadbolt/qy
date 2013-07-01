from counted_file_reader import counted_file_reader

fname=r'C:\Users\Qubit\Data\scan_data\2012_08_06_monday_18h56m32s.counted'
q=counted_file_reader(fname)
print q.get_description()
q.set_patterns(['g', 'm'])

n=1
while n>0:
	n=q.read_chunk()
	