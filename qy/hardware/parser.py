import re

alphabet = 'ABCDEFGHIJKLMNOP'
alphabet_map = dict(zip(alphabet, range(16)))

is_fpga = re.compile(r'\A[A-P]{1,16}\Z')
is_number_4x4 = re.compile(r'\A[0-9]{4}\Z')
is_number_8x2 = re.compile(r'\A[0-9]{2}\Z')
is_special = re.compile(r'\A\*{1,16}\Z')

FPGA = 1
NUMBER = 2
SPECIAL = 3


def sanitize_fpga_pattern(pattern):
    ''' takes an fpga-style pattern and cleans it up '''
    return ''.join(sorted(pattern.upper()))


def get_fpga_pattern(pattern):
    ''' get a numeric value corresponding to an fpga-style pattern '''
    pattern = sanitize_fpga_pattern(pattern)
    out = 0
    for symbol in pattern:
        n = alphabet_map[symbol]
        out = out | (1 << n)
    return out


def get_number_pattern(pattern):
    ''' get a number-resolved pattern from the string '''
    return tuple(map(int, pattern))


def parse_once(string):
    ''' parse a single string as some sort of coincidence pattern'''
    string = string.upper().strip()
    if is_fpga.match(string):
        return (get_fpga_pattern(string), FPGA)
    if is_number_4x4.match(string):
        return (get_number_pattern(string), NUMBER)
    if is_number_8x2.match(string):
        return (get_number_pattern(string), NUMBER)
    if is_special.match(string):
        return (string, SPECIAL)


def parse_pattern_string_comma_delimited(pattern_string):
    ''' parse a list of comma-seperated strings as a list of patterns '''
    pattern_string = pattern_string.strip().split(',')				# split
    patterns = map(parse_once, pattern_string)					# parse each one
    patterns = tuple(set(patterns))									# remove duplicates
    patterns = filter(lambda x: x != None, patterns)
    return patterns


def parse_pattern_list(pattern_list, filt=True):
    ''' parse a list of comma-seperated strings as a list of patterns '''
    patterns = map(parse_once, pattern_list)						# parse each one
    if not filt:
        return patterns										# stop filtering if asked
    patterns = tuple(set(patterns))									# remove duplicates
    patterns = filter(lambda x: x != None, patterns)
    return patterns
