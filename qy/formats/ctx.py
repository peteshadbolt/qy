import os
import json
from qy.util import progressbar
from qy.util import json_no_unicode
from qy.util import timestamp


class CTXException(Exception):

    ''' A generic exception for the CTX file class '''
    pass


class ctx:

    ''' a .CTX file '''

    def __init__(self, filename=None, metadata=None):
        # Get a timestamp
        time_started = timestamp()

        # If no filename is provided, use the timestamp
        if filename:
            if os.path.isdir(filename):
                self.filename = os.path.join(filename, time_started + '.ctx')
            else:
                self.filename = filename
        else:
            self.filename = time_started + '.ctx'

        # If the file exists, we are trying to read from it.
        # Otherwise, we are writing a new file
        self.mode = 'read' if os.path.exists(self.filename) else 'write'

        # If we are writing to a file, put the metadata at the top.
        if self.mode == 'write':
            # Construct some metadata
            if metadata:
                self.metadata = metadata
            else:
                self.metadata = {
                    'label': '%s (no metadata provided)' % self.filename}

            # Automatically add some extra metadata
            self.metadata['timestamp'] = str(time_started)
            if "COMPUTERNAME" in os.environ: 
                self.metadata['computer'] = os.environ['COMPUTERNAME']
            else:
                self.metadata['computer'] = "Unknown computer"

            # Write it to disk
            self.write('metadata', self.metadata)

        # If we are trying to read from the file, we should open it for
        # reading.
        if self.mode == 'read':
            self.read_metadata()

    def stream(self, tag=''):
        '''
        Stream data from the file, filtering for a particular tag of interest
        '''
        f = open(self.filename, 'r')
        for line in f:
            a = line.find(':')
            if a > 0 and line[:a].strip() == tag:
                yield json.loads(line[a + 1:], object_hook=json_no_unicode)

        f.close()

    def read_metadata(self):
        ''' Look for metadata in the file '''
        # TODO: this isn't finished!
        self.metadata = self.stream('metadata').next()

    def write(self, key, data):
        ''' Write '''
        if self.mode != 'write':
            raise CTXException(
                'Cannot write to existing CTX file "%s"' % self.filename)

        data_encoded = json.dumps(data, sort_keys=True)
        f = open(self.filename, 'a')
        s = '%s: %s\n' % (key, data_encoded)
        f.write(s)
        f.close()

    def write_counts(self, data):
        ''' Helper function '''
        self.write('counts', data)

    def __iter__(self):
        return self

    # def next(self):
        #''' Allow use as an iterator (for index, modes in basis)'''
    def __str__(self):
        ''' Convert to a string '''
        s = 'CTX file'
        s += ' %s [%s]\n' % (self.filename, self.mode)
        for key, value in self.metadata.items():
            s += '  %s: %s\n' % (key, value)
        return s
