import counted_file_writer
import time


counted_file_writer.set_time_cutoff_ms(1000)
counted_file_writer.set_window(10)

# set the delays
d=counted_file_writer.array(16)
for i in range(16):
	d[i]=0
counted_file_writer.set_delays(d)

counted_filename=r'C:\Users\Administrator\Data\test_data\spc\out.counted'
spc_filename=r'C:\Users\Administrator\Data\test_data\spc\big.spc'

counted_file_writer.new_counted_file(counted_filename)

t1=time.clock()
counted_file_writer.start_integrating()
counted_file_writer.process_spc(spc_filename)
counted_file_writer.stop_integrating(0)
t2=time.clock()
print 'Time elapsed: %.5f' % (t2-t1)
print counted_file_writer.get_number_rate_4x4(1,0,0,0)
counted_file_writer.close_counted_file()


counted_file_writer.start_integrating()
counted_file_writer.process_spc(spc_filename)

counted_file_writer.stop_integrating(0)
t2=time.clock()
print 'Time elapsed: %.5f' % (t2-t1)
print counted_file_writer.get_number_rate_4x4(1,0,0,0)
