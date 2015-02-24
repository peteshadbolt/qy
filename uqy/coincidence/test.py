import coincidence

coincidence.set_coincidence_window_tb(30)
coincidence.set_time_cutoff_s(1)
coincidence.set_delays_tb([0,0,0,0,0,0,0,0])

for i in range(1, 100, 10):
    coincidence.set_slice_window_ms(i)
    output = coincidence.process_spc("photons.spc")
    #print output["slices"][0], output["slices"][1], output["slices"][-1]
    #print output["times"]
    print "%.2f ms per slice, %d slices" % (i, len(output["slices"]))
    print sum([sum(x.values()) for x in output["slices"]])
    raw_input()

