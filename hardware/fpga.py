import serial
from qy import settings

class fpga:
    """    
    This class talks to a "first generation" Bristol (CQP) FPGA coincidence counter.
    Counts are as follows:
    'A','B','C','D','E','F','G','H','AB','AD','BC','CD','EF','GH','DE','CF','FG','EH','ABCD','CDEF','EFGH','ABCDEFGH'
    """
    
    delays=[0]*8
    finedelays=[0]*8
    modes=[0]*14
    
    def __init__(self, COM=None, callback=None):
        """ Constructor for an FPGA object. Remember that python's COM port indexing starts at zero! """
        if COM==None: COM=settings.lookup('fpga.com')
        self.labels=settings.get('fpga.labels')
        self.serial=serial.Serial()
        self.serial.port=COM
        self.serial.timeout=.1
        self.serial.baudrate=9600
        self.serial.bytesize=serial.EIGHTBITS
        self.serial.parity=serial.PARITY_NONE
        self.serial.stopbits=serial.STOPBITS_ONE
        self.callback=callback
        self.initialize()
        
    def lookup(self, labels, counts):
        """ Pass a list of strings and look up the corresponding coincidences from a list returned by fpga.read(). Order-agnostic (AB=BA) """
        out=[]
        for label in labels:
            for i in range(len(self.labels)):
                if label.upper() == self.labels[i]: out.append(counts[i])
                if len(label)==2:
                    q=label.upper()
                    q=q[1]+q[0]
                    if q == self.labels[i]: out.append(counts[i])
        if len(out)==len(labels):
            return out
        else:
            print 'get_coincidences: Some labels were not found'
            return None
                    
        
    def initialize(self):    
        """ Connects to the serial port, sets up the FPGA. You shouldn't ever need to call this """
        print 'initializing FPGA...',
        self.openSerial()
        for i in range(14):
            self.setMode(i,1)
        for i in range(8):
            self.setDelay(i,20,0)
        self.writeDelays()
        print 'done'

    def setMode(self,combination=0,mode=0):
        """ Sets a counting mode to the FPGA"""
        if combination>=0 and combination<=13: self.modes[13-combination]=mode
        
    def setDelay(self,channel=0,delay=0,finedelay=0):
        """ Sets up FPGA delays. You never need to use this """
        if delay>75: delay=75
        if finedelay>63: finedelay=63
        if channel>=0 and channel<=7:
            self.delays[7-channel]=delay//5
            self.finedelays[7-channel]=finedelay
            
    def writeDelays(self):
        """ Writes a load of settings to the FPGA """
        if self.serial.isOpen():
            # Output the last 2 pairs
            value=self.modes[0]<<2
            value|=self.modes[1]
            
            # Output the modes for the combinations in blocks of 4 pairs of bits
            for i in xrange(2,14,4):
                    value=self.modes[i]<<6
                    value|=self.modes[i+1]<<4
                    value|=self.modes[i+2]<<2
                    value|=self.modes[i+3]
                    self.serial.write(chr(value))
            self.serial.write(chr(value))

            # Output the delays for each channel
            for delay in self.delays:
                self.serial.write(chr(delay))

            # Output the fine delays for each channel
            for finedelay in self.finedelays:
                    self.serial.write(chr(finedelay))
            self.serial.write(chr(250))
            self.serial.write(chr(198))
            self.serial.write(chr(136))
            
    def flush(self):
        self.serial.flushInput()
        
    def get_byte(self):
        out=''
        while len(out)==0:
            out=self.serial.read(1)
        return out
        
    def get_first_byte(self):
        out=''
        while len(out)==0:
            out=self.serial.read(1)
            if self.callback!=None: self.callback('FPGA is waiting for data...')
        return out
        
    def count(self,op=0):
        """ Main function to read a set of values from the FPGA. Returns a list of numbers corresponding to the counts in fpga.labels """
        print 'count'
        counts=self.read()
        q=dict(zip(self.labels,counts))
        return q
            
    def read(self,op=0):
        """ Main function to read a set of values from the FPGA. Returns a list of numbers corresponding to the counts in fpga.labels """
        self.serial.flush()
        counts=[0]*22
        if self.serial.isOpen():
            charFromSerial=self.get_first_byte()#self.get_byte()
            # Look for data
            if len(charFromSerial)==0:
                print "You might want to try plugging the serial cable in"
                return [0]*22
            zeroword=ord(charFromSerial)
            zeroword2=255
            
            while ((zeroword+zeroword2)!=0):
                zeroword2=zeroword
                zeroword=ord(self.get_byte())
        
            # Read the count rates of the 8 channels and the 14 combinations
            for i in xrange(22):
                counts[i]=0
                for j in xrange(0,32,8):
                    # Read and store the counts
                    word=ord(self.get_byte())
                    word<<=j
                    
                    counts[i]|=word
                    # Read the 'address' (and ignore it)
                    address=ord(self.get_byte())
        if counts[21]>100000:
            self.serial.read(2)
            return [0]*22
        return counts
        
    def get_dict(self, op=0):
        """ Main function to read a set of values from the FPGA. Returns a list of numbers corresponding to the counts in fpga.labels """
        counts=self.read()
        return dict(zip(self.labels,counts))
    
    def openSerial(self):
        """ Open the serial port in a silly way """
        if not self.serial.isOpen(): self.serial.open()

    def closeSerial(self):
        """ Close the serial port in a silly way """
        if self.serial.isOpen(): self.serial.close()
        
    def kill(self):
        """ Shut down everything to do with the FPGA """
        print 'closing fpga...',
        self.closeSerial()
        print 'closed.'
