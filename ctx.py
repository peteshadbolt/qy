import os
from StringIO import StringIO
import base64
import gzip
import struct
from qy.util import progressbar

required_metadata = set(['scan_type', 'scan_label'])
data_formats = {
'scan_npoints':[int],
'scan_nloops':[int],
'scan_integration_time':[float],
'scan_close_shutter':[bool],
'scan_dont_move':[bool],
'scan_motor_controller':[int],
'scan_start_position':[float],
'scan_stop_position':[float],
'scan_loop':[int],
'scan_step':[int],
'integration_step': [int],
'motor_controller_update': [int, float]
}

class CTXException(Exception):
    ''' A generic exception for the CTX file class '''
    pass

def format_key_value(key, values):
    ''' Try to format a key-value pair, converting strings to ints etc '''
    try:
        values=[f(v) for f, v in zip(data_formats[key], values)]
        return key, values
    except KeyError:
        return key, values

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

def binary_pattern_to_alphanumeric(pattern):
    ''' Convert a binary-encoded detection event to an alphanumeric string'''
    alphabet='abcdefghijklmnop'
    letters = [alphabet[i] for i in range(16) if (1<<i & pattern)>0]
    if len(letters)==0: print bin(pattern)
    return ''.join(letters)

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
        key,value=struct.unpack('HI', data)
        key = binary_pattern_to_alphanumeric(key)
        output[key]=value

class ctx:
    ''' a .CTX file '''
    def __init__(self, filename, mode=None):
        self.filename=filename
        self.event_list=[]

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
            raise CTXException('Cannot write in read/preview mode!')
        if not required_metadata <= set(metadata.keys()):
            raise CTXException('Certain metadata is required!')

        # Put the metadata in an attribute
        self.metadata=metadata

        # Write the key-value pairs to the file
        f=open(self.filename, 'w')
        f.write('ctx data file\n')
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
        self.filesize=os.path.getsize(self.filename)
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
        line=''
        while line!='end_metadata':
            line = f.readline().strip()

        # Load all the events
        self.event_list=[]
        pb=progressbar(self.filesize, label='Loading %s' % self.filename)
        while line!='':
            line=f.readline()
            pb.update(f.tell())
            items=map(lambda x: x.strip(), line.split(','))

            if items[0]=='motor_controller_update':
                data=(items[0], int(items[1]), float(items[2]))
                self.event_list.append(data)

            elif items[0]=='scan_loop':
                data=(items[0], int(items[1]))
                self.event_list.append(data)

            elif items[0]=='scan_step':
                data=(items[0], int(items[1]))
                self.event_list.append(data)

            elif items[0]=='integration_step':
                data=(items[0], int(items[1]))
                self.event_list.append(data)

            elif items[0]=='start_counts':
                data=f.readline()
                data=decode_counts(data)
                data=('count_rates', data)
                self.event_list.append(data)
            else:
                pass

        pb.finish()
        f.close()
        self.iterator_index=0


    def __len__(self):
        ''' Number of events '''
        return len(self.event_list)


    def __iter__(self): return self
    def next(self):
        ''' Allow use as an iterator (for index, modes in basis)'''
        if self.iterator_index < len(self.event_list)-1:
            cur, self.iterator_index = self.iterator_index, self.iterator_index+1
            return self.event_list[self.iterator_index]
        else:
            self.iterator_index=0
            raise StopIteration()


    def __str__(self):
        ''' Convert to a string '''
        s = 'CTX file'
        s += ' [%s] [%s]\n' % (self.filename, self.mode)
        s += '\n'.join(map(lambda x: '%s: %s' % x, self.metadata.items()))
        if len(self.event_list)>0:
            s += '\n%d events.' % len(self.event_list)
        return s

