''' An example of using CTX '''

from qy.formats import ctx
from qy.analysis.coincidence_counting import pattern_parser as pp
import os
import numpy as np

if __name__=='__main__':
    # Write some test data
    metadata={'label':'This is a test!'}
    output_file=ctx(filename=None, metadata=metadata)
    
    for i in range(3):
        context={'iteration': i, 'sandwich': {'flavour':'egg', 'price':2.50}}
        count_rates={'a':100, 'b':100, 'ab':10, 'abc':1, 'p':666}
        output_file.write('context', context)
        output_file.write('count_rates', count_rates)

    # Read the data back
    input_file=ctx(output_file.filename)
    print input_file

    # Looking at the data, stupid way
    for count_rates in input_file.stream('count_rates'):
        print 'Raw data:', count_rates
        print 'Only "A" clicked:', count_rates['a']
        print 'Only "A" clicked, different method:', pp.parse_coincidence_pattern('A', count_rates)
        print '"A" clicked, don\'t care about other detectors:', pp.parse_coincidence_pattern('a', count_rates)
        print 

    # Looking at the data, simplest way. 
    raw_data=input_file.stream('count_rates')
    get_a_counts = lambda counts: counts['a']
    print 'Simple way to get a column:', map(get_a_counts, raw_data)

    # Looking at the data, clever way
    raw_data=input_file.stream('count_rates')
    get_a_counts = lambda counts: pp.parse_coincidence_pattern('a', counts)
    print 'Clever way to get a column:', map(get_a_counts, raw_data)

    # Getting multiple columns, clever way
    raw_data=input_file.stream('count_rates')
    patterns=['A','b','abc','p'] # these are the patterns I care about
    get_counts = lambda counts: [pp.parse_coincidence_pattern(x, counts) for x in patterns]
    print 'Clever way to get many columns:\n', np.array(map(get_counts, raw_data))

