#!/usr/bin/env python3
"""
Test file for Accumulator
"""
import os
import sys
import unittest
from typing import Any, Tuple, List, Dict, Set

ppath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(ppath)

#import accumulator
from accumulator import Accumulator
#import slot
from slot import Slot

class TestAccumulator(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    @classmethod
    def setUpClass(cls):
        pass
    
    @classmethod
    def tearDownClass(cls):
        pass
    
    def test_1add_slot(self):
        acc: Accumulator = Accumulator('#')
        s5: Slot = Slot(5)
        s5.append("l1,s5")
        acc.add_slot(s5)
        self.assertEqual(set([0, 5, 99]),  acc.slots.keys())
        s5a: Slot = Slot(5)
        s5a.append('l2,s5')
        acc.add_slot(s5a)
        self.assertEqual(set([0, 5, 99]),  acc.slots.keys())
        st = acc.slots[5]
        aa = str(st)
        self.assertEqual('[id:5, len:2, d:(l1,s5, l2,s5)]', str(st))
        s0: Slot = Slot(0)
        s0.append('s0,l1\n')
        acc.add_slot(s0)
        s99: Slot = Slot(99)
        s99.append('s99,l1\n')
        acc.add_slot(s99)

        self.assertEqual(3, len(acc.slots))
        s0 = acc.slots[0]
        self.assertEqual(1, len(s0.data))
        s5 = acc.slots[5]
        self.assertEqual(2, len(s5.data))
        s99 = acc.slots[99]
        self.assertEqual(1, len(s99.data))
        self.assertTrue(5 in acc.slots)
        self.assertFalse(3 in acc.slots)
        acc.add_slot(s99)
        acc.add_slot(s0)
        self.assertEqual(2, len(s99.data))
        self.assertEqual(2, len(s0.data))
        acc.disable_priv_slots()
        acc.add_slot(s99)
        self.assertEqual(2, len(s99.data))
        acc.add_slot(s0)
        self.assertEqual(2, len(s0.data))

    def test_2get_lines(self):
        acc: Accumulator = Accumulator('#')
        s5: Slot = Slot(5)
        s5.append("l1,s5\n")
        acc.add_slot(s5)
        s5a: Slot = Slot(5)
        s5a.append('l2,s5\n')
        acc.add_slot(s5a)
        st = acc.slots[5]
        s0: Slot = Slot(0)
        s0.append('l1,s0\n')
        acc.add_slot(s0)
        s99: Slot = Slot(99)
        s99.append('l1,s99\n')
        acc.add_slot(s99)
        acc.slots[5].data.append('l3,s5\n')
        result = acc.get_lines()

        expected = ['# result from processing !UNSPECIFIED!\n',
                    '\n', '#lines from Slot 0\n',
                    '\n', 'l1,s0\n',
                    '\n', '#lines from Slot 5\n',
                    '\n', 'l1,s5\n',
                    'l2,s5\n',
                    'l3,s5\n',
                    '\n',
                    '#lines from Slot 99\n',
                    '\n',
                    'l1,s99\n',
                    '\n']
        for a, b in zip(expected, result[2:]):
            self.assertEqual(a, b)
        acc.add_file('file1')
        acc.add_file('file2')
        result = acc.get_lines()
        fileinfo = result[3:6]
        self.assertEqual(
            ['# Files included by reference:\n', '#\tfile1\n', '#\tfile2\n'],
            fileinfo)

    def test_6get_fileset(self):
        pass  # ! TODO: implement

    def test_7get_filelist(self):
        acc: Accumulator = Accumulator('#')
        self.assertFalse(acc.get_filelist(full_path=False))
        self.assertFalse(acc.get_filelist(full_path=True))
        self.assertTrue(acc.add_file("file1"))
        self.assertEqual("file1", acc.get_filelist(full_path=False)[0])
        self.assertEqual(1, len(acc.get_filelist(full_path=False)))
        fullpath:str = acc.get_filelist(full_path=True)[0]
        self.assertEqual('file1', os.path.basename(fullpath))
        self.assertEqual(1, len(acc.get_filelist(full_path=True)))
        self.assertFalse(acc.add_file("file1"))
        self.assertTrue(acc.add_file("file2"))
        self.assertFalse(acc.add_file("file2"))
        self.assertEqual(['file1', 'file2'], [
            os.path.basename(n)
            for n in acc.get_filelist(full_path=True)
        ])
        self.assertEqual(['file1', 'file2'], acc.get_filelist(full_path=False))
        self.assertFalse(acc.add_file("./file2"))
        self.assertEqual(2, len(acc.get_fileset()))
        #self.assertTrue(acc.add_file('/file2')) true, but this is like k:\file2
        self.assertTrue(acc.add_file("tests/file2"))
        self.assertTrue(acc.add_file("tests/file3"))
        self.assertTrue(acc.add_file("file3"))
        aa = acc.get_filelist(full_path=True)
        self.assertEqual(5, len(aa))
        expected = [  # ! TODO: this is system dependent
            'M:\\Python\\Python3_packages\\cmdfilebuilder\\file1',
            'M:\\Python\\Python3_packages\\cmdfilebuilder\\file2',
            'M:\\Python\\Python3_packages\\cmdfilebuilder\\tests\\file2',
            'M:\\Python\\Python3_packages\\cmdfilebuilder\\tests\\file3',
            'M:\\Python\\Python3_packages\\cmdfilebuilder\\file3'
        ]

        self.assertEqual(expected, aa)
        self.assertEqual(5, len(acc.get_fileset()))
        ab = acc.get_filelist(full_path=False)
        self.assertEqual(5, len(ab))
        expected = ['file1', 'file2', 'tests\\file2', 'tests\\file3', 'file3']
        self.assertEqual(expected, ab)

    def test_5add_file(self):
        acc: Accumulator = Accumulator('#')
        self.assertTrue(acc.add_file("file1"))
        self.assertTrue(acc.add_file("file2"))
        self.assertFalse(acc.add_file("file2"))
        fs = acc.get_fileset()
        self.assertEqual(2, len(fs))
        self.assertTrue(acc.add_file("file3"))
        self.assertEqual(2, len(fs))
        fs1 = acc.get_fileset()
        self.assertEqual(3, len(fs1))
        self.assertTrue(acc.add_file("file7"))
        self.assertTrue(acc.add_file("file6"))
        for a, b in zip(['file1', 'file2', 'file3', 'file7', 'file6'], acc.get_filelist()):
            self.assertEqual(a, b)

    def test_0creation(self):
        acc: Accumulator = Accumulator('#')
        self.assertEqual(2, len(acc.slots))
        self.assertEqual(set([0, 99]),  acc.slots.keys())
        self.assertEqual(0, len(acc._fileset))
        self.assertFalse(acc.get_fileset())

if __name__ == '__main__':
    unittest.main()
