from datetime import datetime
fmt='%Y_%m_%d_%A_%Hh%Mm%Ss'
def timestamp(): return datetime.strftime(datetime.now(), fmt).lower()
def from_timestamp(s): return datetime.strptime(s, fmt)