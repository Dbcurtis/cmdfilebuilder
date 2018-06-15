#!/usr/bin/env python3
"""
Test file for cmdfilebuilder
"""
import os
from context import cmdfilebuilder
import unittest
import cmdfilebuilder

class TestCmdfilebuilder(unittest.TestCase):

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

    def test_id_comment(self):
        cfb = cmdfilebuilder
        self.assertEqual('#', cfb.id_comment("# a comment"))
        self.assertEqual('##', cfb.id_comment("## a comment"))
        self.assertEqual('#/#', cfb.id_comment("#/# a comment"))
        self.assertEqual('123', cfb.id_comment("123 a comment"))
        self.assertFalse(cfb.id_comment("1234 a comment"))
        self.assertFalse(cfb.id_comment("#acomment"))
        self.assertFalse(cfb.id_comment(" # a comment"))

    def test_id_comment_in_file(self):
        cfb = cmdfilebuilder
        self.assertFalse(cfb._id_comment_in_file(os.path.abspath("cmt_test_not.txt")))
        self.assertEqual('#', cfb._id_comment_in_file(os.path.abspath("cmt_test_1.txt")))
        self.assertEqual('##', cfb._id_comment_in_file(os.path.abspath("cmt_test_2.txt")))
        self.assertEqual('#/', cfb._id_comment_in_file(os.path.abspath("cmt_test_3.txt")))
        self.assertEqual('###', cfb._id_comment_in_file(os.path.abspath("cmt_test_4.txt")))
        self.assertFalse(cfb._id_comment_in_file(os.path.abspath("cmt_test_5.txt")))

    def test_read_the_file(self):
        cfb = cmdfilebuilder
        dictt = cfb.read_the_file("cmt_test_1.txt")
        self.assertEqual('#', dictt.get(cfb.CMT))
        self.assertEqual(9, len(dictt.get(cfb.INL)))
        self.assertEqual(4, len(dictt.get(cfb.DATL)))
        self.assertEqual(5, len(dictt.get(cfb.CMTL)))

    def test_extract_numbered_lines(self):

        def _check_seq(numlinelist, thesplit):
            _aa = [int(j.split(thesplit)[1][0:1]) for i, j in numlinelist]
            for i, j in enumerate(_aa):
                self.assertEqual(i+1, j)

        def _check_nums(numlinelist, thesplit, adj):
            for t in numlinelist:
                [bb] = t[1].split(thesplit, 2)[1:2]
                nd = bb[0:1]
                self.assertEqual(t[0]+adj, int(nd))

        def _test1(inlist):
            lcheck = [(_n, _l) for _n, _l in enumerate(inlist)]
            _check_nums(lcheck, 'line', 1)  #check lines ok
            linedict = cfb.extract_numbered_lines(inlist, None)
            self.assertEqual(lcheck, linedict.get(cfb.INL))

            cmtlines = linedict.get(cfb.CMTL)
            datalines = linedict.get(cfb.DATL)

            self.assertEqual(len(inlist), len(cmtlines) + len(datalines))
            _check_seq(cmtlines, 'cmt')
            _check_seq(datalines, 'data')
            testlines = cmtlines + datalines
            testlines.sort()
            _check_nums(testlines, 'line', 1)  #check reassemble worked
            self.assertEqual(lcheck, testlines)
            return linedict

        cfb = cmdfilebuilder
        inlist = []

        with open("cmt_test_1.txt", 'r') as f:
        #with open(jjj, 'r') as f:
            inlist = f.readlines()

        self.assertEqual(9, len(inlist))
        resultdic = _test1(inlist)
        self.assertEqual('#', resultdic.get(cfb.CMT))
        inlist = []
        with open("cmt_test_2.txt", 'r') as f:
            inlist = f.readlines()

        self.assertEqual(9, len(inlist))
        resultdic = _test1(inlist)
        self.assertEqual('##', resultdic.get(cfb.CMT))
    
    def test_encode_special(self):
        lines = [
            (1, ''), (2, 'This is clean text'),
            (3, '; this is <metadata stuff="morestuff"> not clean text'),
            (4, '; this is <metadata> not clean text'), 
            (5, 'this is <metadata> not <filelist><file>filein</file></filelist></metadata> clean text'), 
            (6, '; this is <metadata> not clean text'), 
            (7, 'this is <metadata> "not" & \'still\' <filelist><file>filein</file></filelist></metadata> clean\'s text'), 
            (8, 'this is <metadata> "not" & \'still\' <filelist><file>aa><>mm</file></filelist></metadata> clean\'s text'),
            (9, '<metadata a="junk">'), 
            (10, '<!-- a comment -->'),
            (11, '<filelist>'),
            (12, '</filelist>'),
            (13, '<filelist></filelist>'),
            (14, '<file></file>'), 
            (15, '<slot></slot>'),
            (16, '<filelist><file></file></filelist>')
        ]

        cfb = cmdfilebuilder
        newlines = cfb._encode_special_xml_char(lines)
        
        decodedlines =  cfb._decode_special_xml_char([l for n, l in newlines])   
        for a, b in zip([l for n, l in lines], decodedlines):
            self.assertEqual(a, b)
        testline = newlines[7][1]
        self.assertTrue('>aa&gt;&lt;&gt;mm' in testline)
        sametestline = cfb._decode_special_xml_char([testline])[0]
        self.assertEqual(lines[7][1], sametestline)
        self.assertEqual(lines[9][1], cfb._decode_special_xml_char([newlines[9][1]])[0])
        self.assertEqual('<filelist>', newlines[10][1])
        self.assertEqual('</filelist>', newlines[11][1])
        self.assertEqual('<filelist><file></file></filelist>', newlines[15][1])
        
   
    def test_decode_special(self): 
        lines = [ ]
        lines.append('')
        lines.append('this is clean text')
        lines.append('&lt;')
        lines.append('&gt;')
        lines.append('&amp;')
        lines.append('&quot;')
        lines.append('&apos;')
        lines.append('test all &lt;one&gt; is &quot;quoted&quot; &amp; it&apos;s ok')                        
               
 
        cfb = cmdfilebuilder
        jj = lines[:]
        kk = cfb._decode_special_xml_char(jj)
        expected =  [ '',  'this is clean text',  '<',
                      '>',  '&',  '"',  "'",
                      'test all <one> is "quoted" & it\'s ok']
        self.assertEqual(expected, kk)
        
    def test_junk(self):
        def sli(t1, t2):
            aa = sorted([t1, t2])
            tp1 = aa[0]
            tp2 = aa[1]
            tp1start = tp1[0]
            tp1end = tp1[1]
            tp2start = tp2[0]
            tp2end = tp2[1]
            if tp2end < tp1start or tp1end <= tp2start:
                return False
            
            if tp1start <= tp2start or tp1end >= tp2end:
                return True
            return False
        
        ts = '0123456789112345678921234567893123456789'
        t1 = (0, len(ts))
        t2 = (10, 20)
        self.assertTrue(sli(t1, t2))
        self.assertTrue(sli(t2, t1))
        t1 = (25, 35)
        self.assertFalse(sli(t1, t2))
        self.assertFalse(sli(t2, t1))
        aa = ts[10:15]
        bb = ts[15:20]
        cc = aa + bb
        self.assertFalse(sli((10, 15), (15, 20) ))
        self.assertFalse(sli( (15, 20),(10, 15) ))
        self.assertTrue(sli((0, 10), (0, 30)))
        self.assertTrue(sli((0, 30), (0, 10)))
        self.assertTrue(sli((0, 10), (9, 30)))
        self.assertTrue(sli((9, 30), (0, 10)))        
        a = 0

    
    def test_split(self):
        cfb = cmdfilebuilder  # assuming the tuplies are lower, higher
        tests = '01234567891123456789212345678931234567890'
        lg = len(tests)
        self.assertEquals(41, lg)
        
        tp1 = tests[0:10]
        tp2 = tests[30:lg]
        self.assertEqual(tests, tests[0:lg])
              
        self.assertEqual('5678921234', tests[15:25])
        self.assertEqual('012345678911234', tests[0:15])
        self.assertEqual('5678931234567890', tests[25:lg])
        
        result = cfb._split((0, lg), (15, 25))
        expected = [(0, 15), (25, lg)]
        self.assertEqual(expected, result)

        result = cfb._split((0, lg), (0, 10))
        expected = [(0, 10), (10, lg)]
        self.assertEquals(expected, result)
        
        result = cfb._split((0, lg), (25, lg))
        expected = [(0, 25), (25, 41)]
        self.assertEqual(expected, result)

    
    def test_intersects(self):
        cfb = cmdfilebuilder  # assuming the tuplies are lower, higher
        self.assertFalse(cfb._intersects([(1, 2), (3, 4), (5, 10)]))
        self.assertFalse(cfb._intersects([(5, 10), (3, 4), (1, 2)]))
        self.assertTrue(cfb._intersects([(1, 10), (5, 15), (20, 30)]))
        self.assertTrue(cfb._intersects([(5, 15), (1, 10), (20, 30)]))
        self.assertTrue(cfb._intersects([(1, 2), (2, 4), (5, 10)]))
        self.assertTrue(cfb._intersects([(1, 4), (3, 7), (5, 10)]))

    def test_gen_xml(self):

        cfb = cmdfilebuilder
        builder = cfb.Cmdfilebuilder('cmt_test_1.txt')
        self.assertFalse(cfb.gen_xml(builder.line_dict))
        self.assertFalse(builder.md_dict)
        builder = cfb.Cmdfilebuilder('md_test_1.txt')
        md_dict = cfb.gen_xml(builder.line_dict)
        self.assertEqual(18, len(md_dict.get('md0')))
        self.assertEqual(25, len(md_dict.get('md1')))
        self.assertEqual(26, len(md_dict.get('md2')))
        self.assertTrue(builder.md_dict)
        self.assertEqual(md_dict, builder.md_dict)


    def test_gendocs(self):

        cfb = cmdfilebuilder
        builder = cfb.Cmdfilebuilder('md_test_1.txt')
        mdtexts = builder.md_dict
        self.assertTrue(builder.gendocs(mdtexts, first=True))
        acc = builder.accum
        slots = acc.slots
        self.assertEqual(7, len(slots))
        files = acc.get_filelist()
        self.assertEqual(4, len(files))
        expected = ['md_test_1.txt', 'cmt_test_1.txt', 'cmt_test_2.txt',
                    'cmt_test_3.txt']
        for a, b in zip(expected, files):
            self.assertEqual(a, b)
        files = acc.get_filelist(full_path=True)
        expected =['K:\\Python3_packages\\cmdfilebuilder\\tests\\md_test_1.txt',
                   'K:\\Python3_packages\\cmdfilebuilder\\tests\\cmt_test_1.txt',
                   'K:\\Python3_packages\\cmdfilebuilder\\tests\\cmt_test_2.txt',
                   'K:\\Python3_packages\\cmdfilebuilder\\tests\\cmt_test_3.txt']
      
        for a, b in zip(expected, files):
            self.assertEqual(a, b)        
        expected = ['\n# defined by Unknown!\n\n', 'md1,s0,l1\n', 'md1.s0,l2\n',
                    '\n# defined by Unknown!\n\n', 'md2,s0,l3\n', 'md2.s0,l4\n',
                    '\n# defined by Unknown!\n\n', 'md3,s0,l5\n', 'md3.s0,l6\n']
        for a, b in zip(expected, slots[0].data):
            self.assertEqual(a, b)
        expected = ['\n# defined by Unknown!\n\n', 'md1,s99,l1\n', 'md1.s99,l2\n',
                    '\n# defined by Unknown!\n\n', 'md2,s99,l3\n', 'md2.s99,l4\n',
                    '\n# defined by Unknown!\n\n', 'md3,s99,l5\n', 'md3.s99,l6\n']
        for a, b in zip(expected, slots[99].data):
            self.assertEqual(a, b)
        expected = ['\n# defined by Unknown!\n\n', 'data md3, slot 10, line 1\n', 'data md3, slot 10, line 2\n']
        for a, b in zip(expected, slots[10].data):
            self.assertEqual(a, b)
        builder = cfb.Cmdfilebuilder('md_test_1.txt', repeater='dlx2-887354')
        
        
        builder = cfb.Cmdfilebuilder('md_test_file3.txt')
        mdtexts = builder.md_dict
        self.assertFalse(builder.gendocs(mdtexts, first=False))
        self.assertEqual('mismatched tag: line 15, column 3', str(builder.last_error) )
        acc = builder.accum        
        
        

    def test_doit(self):

        cfb = cmdfilebuilder
        outpath = 'testout.txt'

            
        def resetoutput():
            try:
                os.remove(outpath)
            except FileNotFoundError:
                pass
            
        def checkoutputsame(f):
            infilelines = []
            with open(f, 'r') as _if:
                infilelines = _if.readlines()

            builder = cfb.Cmdfilebuilder(f)
            resetoutput()

            builder.doit(outpath)
            lines1 = []
            with open(outpath, 'r') as inf:
                lines1 = inf.readlines()
            for a, b in zip(infilelines, lines1):
                self.assertEqual(a, b)

        checkoutputsame('simpletextfile.txt')
        checkoutputsame('cmt_test_1.txt')
        checkoutputsame('md_noslot.txt')
        checkoutputsame('md_nofile1.txt')
        checkoutputsame('md_nofile2.txt')
        
        builder = cfb.Cmdfilebuilder('md_test_file1.txt')
        resetoutput()
        builder.doit(outpath)
        with open(outpath, 'r') as inf:
            lines1 = inf.readlines()
        self.assertEqual(62, len(lines1))
        self.assertTrue('# result from 'in lines1[2])
        self.assertTrue('# Files included by reference'in lines1[3])
        slotsids = [l for l in lines1 if "#lines from Slot " in l]
        self.assertEqual(6, len(slotsids))
        self.assertTrue('Slot 0' in slotsids[0])
        self.assertTrue('Slot 1' in slotsids[1])
        self.assertTrue('Slot 2' in slotsids[2])
        self.assertTrue('Slot 3' in slotsids[3])
        self.assertTrue('Slot 4' in slotsids[4])
        self.assertTrue('Slot 99' in slotsids[5])
        filesids = [l for l in lines1 if "comment test file" in l]
        self.assertEqual(3, len(filesids))
        self.assertTrue('test file 1' in filesids[0])
        self.assertTrue('test file 2' in filesids[1])
        self.assertTrue('test file 3' in filesids[2])

        builder = cfb.Cmdfilebuilder('md_test_file2.txt')
        resetoutput()
        builder.doit(outpath)
        with open(outpath, 'r') as inf:
            lines1 = inf.readlines()        
        
        self.assertEqual(65, len(lines1))
        self.assertTrue('# result from 'in lines1[2])
        self.assertTrue('# Files included by reference'in lines1[3])
        slotsids = [l for l in lines1 if "#lines from Slot " in l]
        self.assertEqual(6, len(slotsids))
        self.assertTrue('Slot 0' in slotsids[0])
        self.assertTrue('Slot 1' in slotsids[1])
        self.assertTrue('Slot 2' in slotsids[2])
        self.assertTrue('Slot 3' in slotsids[3])
        self.assertTrue('Slot 4' in slotsids[4])
        self.assertTrue('Slot 99' in slotsids[5])
        filesids = [l for l in lines1 if "comment test file" in l]
        self.assertEqual(1, len(filesids))
        self.assertTrue('test file 3' in filesids[0])
        bdfcmts =  [l for l in lines1 if "#from md_bad_filelist" in l]
        self.assertEqual(2, len(bdfcmts))
        
        
        
if __name__ == '__main__':
    unittest.main()
    