#!/usr/bin/env python3
"""
Test file for Slot
"""
import os
import sys
#from context import cmdfilebuilder
import unittest
ppath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ppath)
from slot import Slot


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

    def test_1append(self):
        a:Slot = Slot(9)
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

    def test_0creation(self):
        s:Slot = Slot(1)
        #t1 = str(s)
        self.assertEqual('[id:1, len:0, d:]', str(s))
        self.assertTrue(s.is_mt())
        s.append('firstline \n')
        self.assertFalse(s.is_mt())
        #t1 = str(s)
        self.assertEqual('[id:1, len:1, d:(first ...  \n)]', str(s))
        s.append('line 2\n')
        s.append('line 3three\n')
        s.append('line4 is more\n')
        s.append('line56789012345\n')
        #t1 = str(s)
        self.assertEqual(
            '[id:1, len:5, d:(first ...  \n, line 2\n, line  ... e\n, line4 ... e\n, line5 ... 5\n)]',
            str(s))
        s.append('line67890123456\n')
        #t1 = str(s)
        self.assertEqual(
            '[id:1, len:6, d:(first ...  \n,  (...) , line5 ... 5\n, line6 ... 6\n)]',
            str(s))

        s = Slot(2, datain=['line1\n', 'line2\n'])
        #t1 = str(s)
        self.assertEqual('[id:2, len:2, d:(line1\n, line2\n)]', str(s))
        
        try:
            s:Slot = Slot(0)
            s=Slot(99)
            try:
                s=Slot(-1)
                self.fail('should have failed for -1 slot')
            except ValueError as ve2:
                pass
            try:
                s=Slot(100)
                self.fail('should have failed for 100 slot')
            except:
                pass

        except ValueError as ve1:
            self.fail("legal slot unhappy")
 
        


if __name__ == '__main__':
    unittest.main()
