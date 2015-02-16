from datetime import datetime

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

fmt='%Y_%m_%d_%A_%Hh%Mm%Ss'
def timestamp(): return datetime.strftime(datetime.now(), fmt).lower()
def from_timestamp(s): return datetime.strptime(s, fmt)

alphabet_upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
alphabet_lower = 'abcdefghijklmnopqrstuvwxyz'
