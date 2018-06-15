#!/usr/bin/env python3
"""
Test file for Slot
"""
from context import cmdfilebuilder
import unittest
import slot

class TestSlot(unittest.TestCase):
    def setUp(self):
        b = 0
        pass
    
    def tearDown(self):
        b = 1
        pass
    
    @classmethod
    def setUpClass(cls):
        a = 0
        pass
    
    @classmethod
    def tearDownClass(cls):
        a = 1
        pass
    
    def test_append(self):
        a = slot.Slot(9)
        a.append('this is a test\n')
        l = 'this is test 1\n'
        ll = ['this is test 2\n']
        a.append(l)
        a.append(ll)
        self.assertEqual(3, len(a.data))
        tst = a.data[:]
        self.assertTrue('test\n' in tst[0])
        self.assertTrue('test 1\n' in tst[1])
        self.assertTrue('test 2\n' in tst[2])
        
    
    def test_creation(self):
        s = slot.Slot(1)
        t1 = str(s)
        self.assertEqual('[id:1, len:0, d:]', t1)
        self.assertTrue(s.is_mt())
        s.append('firstline \n')
        self.assertFalse(s.is_mt())
        t1 = str(s)
        self.assertEqual('[id:1, len:1, d:(first ...  \n)]', t1)
        s.append('line 2\n')
        s.append('line 3three\n')
        s.append('line4 is more\n')
        s.append('line56789012345\n')
        t1 = str(s)
        self.assertEqual('[id:1, len:5, d:(first ...  \n, line 2\n, line  ... e\n, line4 ... e\n, line5 ... 5\n)]', t1)
        s.append('line67890123456\n')
        t1 = str(s)
        self.assertEqual('[id:1, len:6, d:(first ...  \n,  (...) , line5 ... 5\n, line6 ... 6\n)]', t1)
        
        s = slot.Slot(2, datain=['line1\n', 'line2\n'])
        t1 = str(s)
        self.assertEqual('[id:2, len:2, d:(line1\n, line2\n)]', t1)
        


if __name__ == '__main__':
    unittest.main()