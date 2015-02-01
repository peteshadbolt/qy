from ctx import ctx
import numpy as np
import itertools

meta = {'label': 'hello this is a label'}
c = ctx('C:/Users/Qubit/Desktop', metadata=meta)

for position in np.linspace(0, 1, 20):
    mc_data = []
    mc_data.append({'index': 0, 'position': position})
    mc_data.append({'index': 1, 'position': 100})
    mc_data.append({'index': 2, 'position': 200})
    c.write('motor_controllers', mc_data)

    for integration_step in range(10):
        c.write('integration_step', integration_step)
        counts = {}
        for n in [1, 2, 3]:
            for pattern in itertools.combinations('abcdefghijklmnop', n):
                pattern = ''.join(pattern)
                counts[pattern] = np.random.randint(0, 100)
        c.write_counts(counts)

        # c.write_counts(counts)

the_file = c.filename
c = ctx(the_file)

# for data in c.stream('counts'):
    # print 'read out %d counts' % len(data)

# for event in c:
    # print event
