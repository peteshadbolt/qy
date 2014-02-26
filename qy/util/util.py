import numpy as np
import sys

def dict_to_sorted_numpy(data):
    ''' Convert a dictionary to a sorted numpy array '''
    N=len(data.keys()[0])
    sorted_data=sorted(data.items(), key=lambda pair:pair[0])
    structure=[('labels', int, (N,)), ('counts', float)]
    return np.array(sorted_data, dtype=structure)

def json_no_unicode(data):
    ''' 
    Decode a JSON file into strings instead of unicodes.
    Usage: json.loads(data, object_hook=json_no_unicode)
    '''
    if isinstance(data, dict):
        return {json_no_unicode(key): json_no_unicode(value) for key, value in data.iteritems()}
    elif isinstance(data, list):
        return [json_no_unicode(element) for element in data]
    elif isinstance(data, unicode):
        return data.encode('utf-8')
    else:
        return data

if __name__=='__main__':
    awd
    
    
