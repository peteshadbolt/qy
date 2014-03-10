from qy.hardware.dpc230 import coincidence
import unittest
import os
root=os.path.split(__file__)[0]
test_filename=os.path.join(root, 'second.spc')

class CoincidenceTests(unittest.TestCase):
    def test1(self):
        window=coincidence.set_window(5)
        self.failUnless(window==5)
        print window

if __name__=='__main__':
    unittest.main()
