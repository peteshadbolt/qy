import os

required_metadata = set(['scan_type', 'scan_label'])
metadata_formats = {
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
    pass

class counted_file:
    ''' a .COUNTED file '''
    def __init__(self, filename, mode=None):
        self.filename=filename

        # Choose mode automatically 
        self.mode=mode
        if not self.mode in ['read', 'write']:  
            self.mode='read' if os.path.exists(self.filename) else 'write'
        if self.mode=='read': self.load_metadata()

    def write_metadata(self, metadata):
        ''' Write metadata to the file '''
        # Check for bad behaviour 
        if self.mode=='read':
            raise CountedFileException('Cannot write in read mode!')
        if not required_metadata <= set(metadata.keys()):
            raise CountedFileException('Certain metadata is required!')

        # Put the metadata in an attribute
        self.metadata=metadata

        # Write the key-value pairs to the file
        f=open(self.filename, 'wa')
        f.write('counted_file\n')
        for key, value in metadata.items():
            s='%s : %s\n' % (key, value)
            f.write(s)
        f.write('end_metadata\n\n')
        f.close()

    def load_metadata(self):
        ''' Load the metadata '''
        self.metadata={}
        f=open(self.filename, 'r')
        for line in f:
            line=map(str.strip, line.split(':'))
            if len(line)==2:
                key, value=line
                try:
                    value=metadata_formats[key](value)
                except KeyError:
                    pass
                self.metadata[key]=value
            elif line == 'end_metadata': 
                f.close()
                return

    def __str__(self):
        ''' Convert to a string '''
        s = 'COUNTED file'
        s += ' [%s] [%s]\n' % (self.filename, self.mode)
        s += '\n'.join(map(lambda x: '%s: %s' % x, self.metadata.items()))
        return s


if __name__=='__main__':
    c = counted_file('/home/pete/Desktop/test.counted', 'write')
    c.write_metadata({'scan_type':'scan', 'scan_label':'test label', 'scan_npoints':5})

    c = counted_file('/home/pete/Desktop/test.counted')
    print c

