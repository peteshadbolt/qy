import unittest
from qy.formats import ctx
import os
import struct
from random import randint
root=os.path.split(__file__)[0]
test_filename=os.path.join(root, 'test.ctx')

N=1000

class CountedTests(unittest.TestCase):
    def testReadWrite(self):
        # Try building a CTX file
        c = ctx(test_filename, 'write')
        c.write_metadata({'scan_type':'scan', 'scan_label':'test label', 'scan_npoints':5})

        # How fast can we write 100 chunks? (Answer: fast enough)
        from random import randint

        print 'Writing...'
        for i in range(N):
            # Generate dummy data
            s=''
            for i in range(100):
                s+=struct.pack('HI', i+1, 3*(i+1))
                #s+=struct.pack('HI', randint(1, 2**8), randint(0,10))
                #s+=struct.pack('HI', randint(1, 16), randint(0,1000))

            # Dump it to disk
            c.write_list(['scan_step', 1])
            c.write_list(['motor_controller_update', 0, i/200.])
            c.write_list(['motor_controller_update', 1, i/100.])
            c.write_list(['motor_controller_update', 1, i/100.])
            c.write_counts(s)

        # Try loading a CTX file
        print 'Reading...'
        c = ctx(test_filename, mode='read')
        nmcs=0
        for event in c:
            if event[0]=='motor_controller_update': nmcs+=1
            if event[0]=='count_rates':
                self.failUnless(event[1]['ab']==9)
        self.failUnless(nmcs==3*N)

if __name__=='__main__':
    unittest.main()
