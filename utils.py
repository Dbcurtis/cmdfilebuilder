#!/usr/bin/env python3
"""
TBD
"""
import logging
import logging.handlers
import collections

from constants import SLOT_INITIAL, SLOT_FINAL, XMLTERMS, METADATA_PAT, \
     CMTL, DATL, INL, CMT, METADATA, SLOT, FILELIST, FILE, SID, XMLSEQ, XMLSEQR

LOGGER = logging.getLogger(__name__)

def id_comment(line):
    """id_comment(line)

    return the comment character(s) from the first characters of the line

    returns None if no comment character, the comment character(s)
    length is > 3 or if the comment character(s) contains a ">" or "<"

    """
    result = None
    if line:
        cmt = line.split(' ', 1)[0].strip()
        if cmt and len(cmt) <= 3 and not ('>' in cmt or '<' in cmt):
            result = cmt
    LOGGER.info('Comment seq is "%s"', cmt)
    return result

def _id_comment_in_file(file):
    """_id_comment_in_file(file)

    return the comment character(s) from the FIRST line of the file
    returns None if file cannot be opened, if the comment character(s)
    length is > 3 or if the comment character(s) contains a ">" or "<"

    not used except for testing

    """
    result = None
    line = None
    try:
        with open(file, 'r', encoding='utf-8') as _f:
            line = _f.readline()
        result = id_comment(line)
    except FileNotFoundError:
        print("file {} not found when detecting comment character".format(file))

    return result

def extract_numbered_lines(inlist, cmt):
    """extract_numbered_lines(inlist)

    inlist is a list of lines
    if the first line does not define a comment character sequence
    an assertion is raised

    returns a dict with the following keys. The values in the dict are tuples
    of the integer line number and the line.  The line number starts at 0

    CMTL = 'cmtlines' -> lines starting with the comment character(s)
    DATL = 'datalines' -> lines not starting with comment characters()
    INL = 'lines' -> lines as read from the file
    CMT = 'commentid' -> comment character(s)

    The following snippit plases the numbered line tuples in order
        testlines = cmtline_tuples + dataline_tuples
        testlines.sort()

    """
    if cmt:
        _cmt = cmt
    else:
        _cmt = id_comment(inlist[0])

    if _cmt:
        _cmtl_list = [(_i, _l) for _i, _l in enumerate(inlist) if  _l.startswith(_cmt)]
        _datl_list = [(_i, _l) for _i, _l in enumerate(inlist) if not _l.startswith(_cmt)]
    else:
        _cmtl_list = []
        _datl_list = [(_i, _l) for _i, _l in enumerate(inlist)]
    _inl_list = [(_i, _l) for _i, _l in enumerate(inlist)]
    return {CMTL: _cmtl_list, DATL: _datl_list, INL: _inl_list, CMT: _cmt,}

def read_the_file(infile, cmt=None):
    """read_the_file(infile)

    Reads the file and returns a dict with keys:
    CMTL = 'cmtlines' -> lines starting with the comment character(s)
    DATL = 'datalines' -> lines not starting with comment characters()
    INL = 'lines' -> lines as read from the file
    CMT = 'commentid' -> comment character(s)

    Each of the xxL keys returns a list of tuples t[0] is the integer line number
    and t[1] is the line
    """
    with open(infile, 'r') as _f:
        _inlist = _f.readlines()

    return extract_numbered_lines(_inlist, cmt)

def _intersect(tp1, tp2):
    """_intersect(tp1, tp2)

    tp1 and tp2 tuples consiste of two numbers with the smaller number at 0 and
    the larger number at 1

    checks if two tuples intersect (not in the same way that splitting does)

    returns True if intersect, False otherwise
    """
    tp2above = tp1[1] < tp2[0]
    tp2below = tp2[1] < tp1[0]
    return not (tp2above or tp2below)

def _intersects(tlist):
    """_intersects(tlist)

    tlist is a list of tuples each of which consiste of two numbers with the smaller number at 0 and
    the larger number at 1

    returns True if the list of tuples have an intersection
    False otherwise

    """
    result = False
    match = tlist[:]

    for _t1 in tlist:
        for _t2 in match:
            if _t1 != _t2:
                result = _intersect(_t1, _t2)
            if result:
                break
        if result:
            break
    return result

def xmlmap(mydic, lines):
    """xmlmap(mydic, lines)

    mydic is the dictionary for the conversion
    lines is a list of strings
    returns a list of strings that result from the application of the map
    """
    result = []
    for _lin in lines:
        _wl = _lin
        for _a, _b in mydic.items():
            _wl = _wl.replace(_a, _b)
        result.append(_wl)
    return result

def _split(intersected, intersector):
    """_split(intersected, intersector)

    """
    pieces = []
    iedstart = intersected[0]
    iedend = intersected[1]
    iorstart = intersector[0]
    iorend = intersector[1]

    atstart = iedstart == iorstart
    atend = iedend == iorend

    if atstart and atend:
        return []

    if not (atstart or atend):
        pieces.append((iedstart, iorstart))
        pieces.append((iorend, iedend))
    else:
        if atstart:
            pieces.append((iorstart, iorend))
            pieces.append((iorend, iedend))
        else:
            pieces.append((iorstart, iorend))
            pieces.append((iedstart, iorstart))
    return sorted(pieces)

def removehits(ltup, hits):
    """removehits(ltup,hits)

    """
    def _slice_intersect(tplin):
        """_slice_intersect(tplin)

        tplin is a tuple
        """
        _ = sorted(tplin)
        tp1 = _[0]
        tp2 = _[1]
        if tp1[1] == tp2[0]:
            return False
        tp1start = tp1[0]
        tp1end = tp1[1]
        tp2start = tp2[0]
        tp2end = tp2[1]
        if tp2end < tp1start or tp1end <= tp2start:
            return False

        if tp1start <= tp2start or tp1end >= tp2end:
            return True

        return False

    working = ltup[:]
    hitq = collections.deque(hits)
    fragments = []
    while hitq:
        hit = ()
        try:
            hit = hitq.popleft()
        except:
            break
        done = False
        while not done:
            hadhit = False
            for partial in working:
                if _slice_intersect((partial, hit)):
                    working = _split(partial, hit)
                    try:
                        fragments.append(working[0])
                        working = [working[1]]
                    except IndexError:
                        LOGGER.error("IndexError... ignored")

                    hadhit = True
                    break

            done = not hadhit

    fragments += working
    #remove errors from the list
    fixedfrags = [t for t in fragments if not t in hits]
    return fixedfrags

def _encode_special_xml_char(nmd):
    """_encode_special_xml_char(nmd)

    nmd is a list of numbered xml line tuples
    returns a list of numbered xml line tuples with the special characters encoded

    special XML characters are >, <, &, ", and '
    corrosponding to &gt;, &lt;, &amp; &quote; and &apos;
    if these characters exist in the text processed by the XML parser,
    all hell breaks loose, they need to be encoded and decoded approrpately
    """
    def _process_hits(line):
        """_process_hits(line)

        line is a string

        finds recognized XML metadata leaving non-XML data
        scans the non-XML data to encode special XML sequences
        returns a rebuilt line
        """
        md_locations = []  #a list of tuples ((start,end), group0)
        idx = 0
        while True:  #generates locations where there is metadata
            res = METADATA_PAT.search(line, idx)
            if res:
                span = res.span()
                md_locations.append((span, res.group(0)))
                idx = span[1]
                continue
            break
        #now remove the metadata locations from the line
        hits = [s[0] for s in md_locations]
        nonhits = removehits([(0, len(line))], hits)
        nometadatalines = [(t, _encode_clean_line(line[t[0]:t[1]])) for t in nonhits]
        #generate the line segments
        partials = [l for _, l in sorted(nometadatalines + md_locations)]
        #and rebuild the line and return it
        return ''.join(partials)

    def _encode_clean_line(line):
        return xmlmap(XMLSEQR, [line])[0]

    result = []
    for _ in nmd:
        _num = _[0]
        _line = _[1]
        if [_ for _ in XMLTERMS if _ in _line.lower()]:
            result.append((_num, _process_hits(_line)))
        else:
            result.append((_num, _encode_clean_line(_line)))
    return result


def _decode_special_xml_char(lines):
    """_decode_special_xml_char(nmd)

    lines is a list of xml strings
    returns decoded lines recreating the special encoded characters.

    see the documentation for _encode_special_xml_char
    """
    return xmlmap(XMLSEQ, lines)

def gen_xml(numbered_lines):
    """gen_xlm(numbered_lines)

    Extracts the XML from comments in the numbered lines.
    """
    def _fixnewlines(numbered_lines):
        """_fixnewlines(numbered_lines)

        numbered_lines is a list of tuples [0] the line number, and [1] the line
        """
        #result = []
        orf = {True: lambda _a, _b: (_a, _b), False:lambda _a, _b: (_a, _b+'\n'),}
        #for _n, _l in numbered_lines:
            #tup = orf.get(_l.endswith('\n'))(_n, _l)
            #result.append(tup)
        result = [orf.get(_l.endswith('\n'))(_n, _l) for _n, _l in numbered_lines]
        return result

    def _stripcmt(cmt, _):
        return _.split(cmt)[1].strip()

    def _extract_line_tuples(tpl, numlines):
        return  [_ for _ in numlines if _[0] in range(tpl[0], tpl[1]+1)]

    result = None
    mdstart = [_n for _n, _l in numbered_lines.get(CMTL) if '<metadata' in _l]
    mdend = [_n for _n, _l in numbered_lines.get(CMTL) if '</metadata>' in _l]
    # verify ranges are ok
    if mdstart and mdend:
        assert len(mdstart) == len(mdend), 'metadata tag not balenced'
        md_line_ranges = [(s, e) for s, e in zip(mdstart, mdend)]
        for _ in md_line_ranges:
            assert _[0] >= 0, 'negative starting line number'
            assert _[1] >= 0, 'negative ending line number'
            assert _[0] <= _[1], 'line numbers out of sequence'

        if _intersects(md_line_ranges):
            LOGGER.critical('intersecting <metadata></metadata> blocks are not allowed')
        assert not _intersects(md_line_ranges), \
               'intersecting <metadata></metadata> blocks are not allowed'
        # extract the metadata info from the comments
        newkeynum = 0
        metadata_linetuples = {}  #key as md# where # goes from 0 up
        for _ in md_line_ranges:
            metadata_linetuples['md'+str(newkeynum)] = [
                (n, _stripcmt(numbered_lines.get(CMT), l))
                for n, l in _extract_line_tuples(_, numbered_lines.get(CMTL))
            ]
            newkeynum += 1
        result = {}
        #combine metadata comments with included text
        #encode the data
        #remove the numbers from the lines
        for _mditem in metadata_linetuples.items():
            lst = _mditem[1]  #get md info for md block
            keys = sorted(dict(lst).keys())  #get line numbers
            totset = set([i for i in range(keys[0], keys[-1]+1)])
            lst += [t for t in numbered_lines.get(INL) if t[0] in totset - set(keys)]
            lst = _fixnewlines(lst)
            result[_mditem[0]] = [l for n, l in _encode_special_xml_char(sorted(lst))]
    return result
