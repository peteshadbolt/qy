import time, sys
from uqy.dpc230 import coincidence_counter
from uqy.ctx import ctx
from uqy.smc100 import smc100
import uqy.settings
import numpy as np
import os
from pprint import pprint

""" 
An example of short integration times, without a GUI 
"""


if __name__=="__main__":
    
    def handle_data((key, value)):
        """ Define how to handle data coming from the counting system """
        if key=="coincidence_data":
            # We got some count rates
            count_rates=value["count_rates"]
            # together with the context in which they were measured
            context=value["context"]

            # Print out some stuff
            print "Recieved data:"
            pprint(count_rates)
            print "Context"
            pprint(context)
            
            # Write that data to disk
            output_file.write("context", context)
            output_file.write("count_rates", count_rates)

        elif key=="dpc230_status":
            #print value
            pass


    # START HERE 
    # Get a file ready to store data
    metadata={"label":"This is a test!", "mood":"hungry for knowledge"}
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    output_file=ctx(data_dir, metadata=metadata)

    # Connect to the counting gear and configure it
    counter=coincidence_counter(callback=handle_data)
    counter.set_delays_tb([0]*16)
    counter.set_integration_time_s(1)
    counter.set_slice_time_ms(100)

    # Count ten times
    for i in range(10):
        counter.count({"test":i})

    # Collect and log the last piece of data from the postprocessor
    counter.collect()

    # Close connections to hardware
    counter.kill()

