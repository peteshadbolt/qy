import os
from StringIO import StringIO
import base64
import gzip
import struct

required_metadata = set(['scan_type', 'scan_label'])
data_formats = {
'scan_npoints':int,
'scan_nloops':int,
'scan_integration_time':float,
'scan_close_shutter':bool,
'scan_dont_move':bool,
'scan_motor_controller':int,
'scan_start_position':float,
'scan_stop_position':float,
'scan_loop':int,
'scan_step':int,
'integration_step':int,
}

class CountedFileException(Exception):
    ''' A generic exception for the counted file class '''
    pass

def format_key_value(key, value):
    ''' Try to format a key-value pair, converting strings to ints etc '''
    try:
        return key, data_formats[key](value)
    except KeyError:
        return key, value

def encode_counts(binary_string):
    ''' Encodes a binary blob of countrates to a text format for storage '''
    # GZIP the data
    zipped = StringIO()
    zipper = gzip.GzipFile(mode='wb', fileobj=zipped)
    zipper.write(binary_string)
    zipper.close()

    # Base 64 encode the string
    s = base64.b64encode(zipped.getvalue())
    return s

def decode_counts(data_string):
    ''' Decodes a text blob to a dictionary of count rates '''
    # Base 64 decode the string
    s = base64.b64decode(data_string)

    # unGZIP the data
    zipped = StringIO(s)
    zipper = gzip.GzipFile(mode='r', fileobj=zipped)

    # Build a dictionary of countrates
    output={}
    while True:
        data=zipper.read(8)
        if data=='': return output
        data=struct.unpack('hi', data)

class counted_file:
    ''' a .COUNTED file '''
    def __init__(self, filename, mode=None):
        self.filename=filename

        # Choose mode automatically 
        self.mode=mode
        if not self.mode in ['read', 'write', 'preview']:  
            self.mode='preview' if os.path.exists(self.filename) else 'write'

        if self.mode=='preview': 
            self.load_metadata()
        elif self.mode=='read': 
            self.load_metadata()
            self.load_in_full()

    def write_metadata(self, metadata):
        ''' Write metadata to the file '''
        # Check for bad behaviour 
        if self.mode!='write':
            raise CountedFileException('Cannot write in read/preview mode!')
        if not required_metadata <= set(metadata.keys()):
            raise CountedFileException('Certain metadata is required!')

        # Put the metadata in an attribute
        self.metadata=metadata

        # Write the key-value pairs to the file
        f=open(self.filename, 'w')
        f.write('counted_file\n')
        for key, value in metadata.items():
            s='%s, %s\n' % (key, value)
            f.write(s)
        f.write('end_metadata\n\n')
        f.close()


    def write_list(self, data):
        ''' Write '''
        f=open(self.filename, 'a')
        s=', '.join(map(str, data))+'\n'
        f.write(s)
        f.close()


    def write_counts(self, binary_string):
        ''' Write down some countrates as a binary string '''
        # TODO: should probably wrap this in a micro-format
        # Compress the data
        s=encode_counts(binary_string)

        # Write it to disk
        f=open(self.filename, 'a')
        f.write('start_counts\n' + s + '\nend_counts\n\n')
        f.close()


    def load_metadata(self):
        ''' Load the metadata '''
        self.metadata={}
        f=open(self.filename, 'r')
        for line in f:
            line=map(str.strip, line.split(','))
            if len(line)==2:
                key, value=format_key_value(line[0], line[1])
                self.metadata[key]=value
            elif line == 'end_metadata': 
                f.close()
                return
        f.close()


    def load_in_full(self):
        ''' Load the file in full, with an optional callback for progress '''
        # Jump to the end of the metadata
        f=open(self.filename, 'r')
        self.events=[]
        line=''
        while line!='end_metadata':
            line = f.readline().strip()

        while line!='':
            line=f.readline()
            entries=map(lambda x: x.strip(), line.split(','))

            if entries[0]=='motor_controller_update':
                pass
            if entries[0]=='start_counts':
                data=f.readline()
                data=decode_counts(data)

        f.close()

    def __str__(self):
        ''' Convert to a string '''
        s = 'COUNTED file'
        s += ' [%s] [%s]\n' % (self.filename, self.mode)
        s += '\n'.join(map(lambda x: '%s: %s' % x, self.metadata.items()))
        return s


if __name__=='__main__':

    # Try building a counted file
    c = counted_file('test.counted', 'write')
    c.write_metadata({'scan_type':'scan', 'scan_label':'test label', 'scan_npoints':5})

    # How fast can we write 100 chunks? (Answer: fast enough)
    from random import randint
    # Generate dummy data
    s=''
    for i in range(10):
        s+=struct.pack('hi', 0, 0)
    
    # Dump it to disk
    for i in range(100):
        c.write_list(['motor_controller_update', 0, .5])
        c.write_list(['motor_controller_update', 0, .5])
        c.write_counts(s)

    # Try loading a counted file
    c = counted_file('test.counted', mode='read')
    print c



