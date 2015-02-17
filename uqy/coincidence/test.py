import coincidence

print "Testing..."
coincidence.set_coincidence_window_tb(30)
coincidence.set_slice_window_ms(2)
coincidence.set_time_cutoff_s(0.5)
coincidence.set_delays_tb([0,0,0,0,0,0,0,0])
coincidence.wtf()
output = coincidence.process_spc("photons.spc")
print output
print "Done"

