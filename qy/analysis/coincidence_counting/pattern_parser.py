import re

def parse_coincidence_pattern(pattern, data):
    ''' Return the sum over all terms in a dataset which match a given regular expression '''
    filtered=[value for key, value in data.items() if re.match(pattern, key)]
    return sum(filtered)
