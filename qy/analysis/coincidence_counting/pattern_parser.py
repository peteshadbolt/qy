import re

def parse_coincidence_pattern(pattern, data):
    ''' Return the sum over all terms in a dataset which match a given regular expression '''
    try:
        filtered=[value for key, value in data.items() if re.search(pattern, key)]
        return sum(filtered)
    except re.error:
        return 0
