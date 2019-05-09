#!/usr/bin/env python3
"""constants.py

Contains constants
"""
import re

# special slots
SLOT_INITIAL = 0
SLOT_FINAL = 99

XMLTERMS = ('<metadata', '</metadata>', '<slot', '</slot>',
            '<filelist>', '</filelist>', '<file>', '</file>',
            '<!--', )

METADATA_PAT = re.compile(r'\</?([!]--|metadata|slot|file|filelist).*?\>',
                          re.IGNORECASE | re.MULTILINE | re.DOTALL)

# commonly used text
CMTL = 'cmtlines'
DATL = 'datalines'
INL = 'lines'
CMT = 'commentid'

METADATA = 'metadata'
SLOT = 'slot'
FILELIST = 'filelist'
FILE = 'file'
SID = 'sid'

# some translations from & char to ascii char
# the position of the & and the &amp; keys is importaint
XMLSEQ = {'&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'", '&amp;': '&', }
XMLSEQR = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;', }

MDRAF = '-887354'
MDKNOWNRS = ('dlx2', 'club', 'rlc1', 'rlc1+')
LEGAL_SLOT_R = range(SLOT_INITIAL, SLOT_FINAL)
FP = 0
DP = 1
BN = 2
