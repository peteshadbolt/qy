import re

def absolute(pattern, data):
    ''' Only an exact match is okay '''
    matcher = lambda key: pattern == set(key)
    matches = filter(matcher, data.keys())
    return sum([data[key] for key in matches])

def contains(pattern, data):
    ''' Data must contain the requested pattern'''
    matcher = lambda key: pattern.issubset(set(key))
    matches = filter(matcher, data.keys())
    return sum([data[key] for key in matches])

def wildcard(pattern, data):
    ''' Just count photons '''
    matcher = lambda key: len(pattern) == len(key)
    matches = filter(matcher, data.keys())
    return sum([data[key] for key in matches])

def parse_coincidence_pattern(pattern_string, data):
    ''' Return the sum over all terms in a dataset which match a given regular expression '''
    count=0
    pattern=set(pattern_string.lower())
    if re.match('[A-Z]+', pattern_string):
        return absolute(pattern, data)
    elif re.match('[a-z]+', pattern_string):
        return contains(pattern, data)
    elif re.match('\*+', pattern_string):
        return wildcard(pattern_string, data)
    else:
        return 0
