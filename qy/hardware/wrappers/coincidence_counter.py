from multiprocessing import Process, Pipe 
import time, sys
from qy.hardware import dpc230
from qy.analysis import coincidence
import winsound


class postprocessor:
    ''' Processes timetags from the DPC230 in parallel with other tasks.'''

    def __init__(self, pipe=None):
        ''' Constructor '''
        # Set up
        self.pipe=pipe
        self.poll = (lambda x:False) if pipe==None else pipe.poll
        self.send = (lambda x: x) if pipe==None else pipe.send
        self.recv = (lambda x: x) if pipe==None else pipe.recv

        # Connect to the DPC230 in simulation mode
        self.dpc_post=dpc230('postprocessing')

        # Start listening
        self.listen()

    def listen(self):
        ''' Constantly listen for messages from the top level process. '''
        while self.poll(None):
            message=self.recv()
            self.handle_message(message)


    def shutdown(self, *args):
        ''' Shut down carefully '''
        print 'Shut down the postprocessor'
        sys.exit(0)


    def handle_message(self, message):
        ''' Handle a message coming from the client ''' 
        if message[0]=='tdc': 
            self.handle_tdc(message)
        elif message[0]=='shutdown': 
            self.shutdown()
        elif message[0]=='delays': 
            coincidence.set_delays(message[1])


    def handle_tdc(self, message):
        ''' Process some timetags '''
        # Parse the message
        tag, data=message
        context = data['context']
        tdc1, tdc2 = data['tdc1'], data['tdc2']

        # Heavy lifting is here
        spc_filename = self.dpc_post.convert_raw_data(tdc1, tdc2)
        count_rates=coincidence.process_spc(spc_filename)
        data={'context':context, 'count_rates': count_rates}
        self.send(('count_rates', data))


class threaded_coincidence_counter:
    ''' 
    An asynchrous coincidence counting system.
    Data aquisition and postprocessing run in parallel subprocesses.
    '''
    def __init__(self, callback=None, dpc_callback=None, timeout=2):
        ''' Initialize both sub-processes '''
        # Connect to the DPC230
        self.dpc230 = dpc230('hardware', dpc_callback)

        # Interface
        self.callback=callback if callback else sys.stderr.write
        self.timeout=timeout

        # Start up the postprocessing process and build the communication network
        self.pipe, post_pipe = Pipe()
        self.post = Process(target=postprocessor, name='post', args=(post_pipe,))
        self.post.start()

    def count(self, integration_time, context):
        ''' Count coincidences '''
        # Count for the specified amount of time
        tdc1, tdc2 = self.dpc230.count(integration_time)

        # Send those timetags off to the postprocessor
        self.pipe.send(('tdc', {'tdc1':tdc1, 'tdc2':tdc2, 'context':context}))
        while self.pipe.poll():
            data = self.pipe.recv()
            if data[0]=='count_rates': self.callback(data)
                

    def collect(self):
        if self.pipe.poll(self.timeout):
            data = self.pipe.recv()
            if data[0]=='count_rates': self.callback(data)


    def shutdown(self, *args):
        ''' Shut down carefully '''
        print 'Shut down the DPC230'
        self.pipe.send(('shutdown', None))
        self.dpc230.kill()
        

if __name__=='__main__':
    def receive_counts(data):
        print '\nTop level received data:' 
        print data

    c=threaded_coincidence_counter(callback=receive_counts)

    for position in range(5):
        c.count(1, {'position': position}) 
    c.collect()

    c.shutdown()


