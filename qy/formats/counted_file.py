import os

required_metadata= set(['scan_type', 'scan_label'])

class CountedFileException(Exception):
    pass

class counted_file:
    ''' a .COUNTED file '''
    def __init__(self, filename, mode=None):
        self.filename=filename
        self.mode=mode
        if not self.mode in ['read', 'write']:  
            self.mode='read' if os.path.exists(self.filename) else 'write'

        if self.mode=='read': self.load_metadata()

    def write_metadata(self, metadata):
        ''' Write metadata to the file '''
        if self.mode=='read':
            raise CountedFileException('Cannot write in read mode!')
        if not required_metadata <= set(metadata.keys()):
            raise CountedFileException('Certain metadata is required!')

        f=open(self.filename, 'wa')
        for key, value in metadata.items():
            print 'awd'

    def load_metadata(self):
        ''' Load the metadata '''
        pass

    def __str__(self):
        ''' Convert to a string '''
        s = 'COUNTED file'
        s += ' [%s] [%s]' % (self.filename, self.mode)
        return s


if __name__=='__main__':
    c = counted_file('/home/pete/Desktop/test.counted', 'write')
    c.write_metadata({'scan_type':'scan', 'scan_label':'test label'})
    print c

