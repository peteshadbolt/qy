import coincidence as c
from glob import glob
import re

help(c)
c.set_window(5)
c.set_time_cutoff(9)
c.set_delays([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
data = c.process_spc('minute.spc')


def search(dictionary, regex):
    ''' Search a dictionary for matching stuff, and return the sum '''
    result = 0
    for key, value in dictionary.items():
        if re.match(regex, key):
            result += value
    return result

# print search(data, '.$')
# print search(data, '.')
# print search(data, '..')
# print search(data, '.') - search(data, '.$')
print data['ab']
print search(data, '.*a.*b.*')
# for key, value in data.items():
    # print key, value
