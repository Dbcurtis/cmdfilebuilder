#!/usr/bin/env python3
""" cmdfilebuilder

    See the README.rst file
"""

import os
import argparse
import logging
import logging.handlers

from xml.dom.minidom import parseString
import xml.dom.minidom
import accumulator
import slot
from constants import INL, CMT, FP, DP, SLOT_INITIAL, SLOT_FINAL, CMTL, DATL
from utils import id_comment, _id_comment_in_file, extract_numbered_lines, \
    read_the_file, _intersect, _intersects, _encode_special_xml_char, \
    _decode_special_xml_char, _split, gen_xml

LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/cmdfilebuilder'

if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)

LF_HANDLER = logging.handlers.RotatingFileHandler(
    ''.join([LOG_DIR, LOG_FILE, ]),
    maxBytes=100000,
    backupCount=5,
)

LC_HANDLER = logging.StreamHandler()
LF_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
LC_FORMATTER = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
THE_LOGGER = logging.getLogger()


class Cmdfilebuilder:
    """Cmdfilebuilder

    Class to process the input file(s)
    """

    def __init__(self, _filepath, repeater=""):
        """Cmdfilebuilder(_filepath, repeater="")

        Instantiates a builder, reading the data from the _filepath as the
        master file.

        repeater can be used to specify the repeater controller
        """
        filepath = os.path.abspath(_filepath)
        self.fileinfo = (filepath, os.path.dirname(
            filepath), os.path.basename(filepath))
        self.line_dict = read_the_file(filepath)
        msg = 'File: {}, lines read: {}'.format(
            filepath, len(self.line_dict[INL]))
        LOGGER.debug(msg)
        self.md_dict = gen_xml(self.line_dict)  # metadata dictionary
        self.repeater = repeater
        self.accum = accumulator.Accumulator(self.line_dict[CMT])
        self.accum.add_file(_filepath)
        self._child_file_warning = True
        self.last_error = None

    def __str__(self):
        return 'CmdFileBuilder: {}'.format(self.fileinfo[2])

    def gendocs(self, _md_dict, first=False, infile=None):
        """gendocs(_md_dict, first=TF, infile=filename)

        _md_dict is 
        infile is the filename to be logged
        first if True enables <filelist> processing, if False will flag as an error
        if filelist is present
        returns a True if ok, False otherwise
        """
        
        infilea = infile
        if not infile:
            infilea = 'Unknown!'

        dom_trees = {}

        for key in sorted(_md_dict.keys()):
            try:
                # parse the XML from the extracted comments
                dom_trees[key] = parseString(" ".join(_md_dict.get(key)))

            except xml.parsers.expat.ExpatError as _er:
                LOGGER.error('XML error %s', str(_er))
                self.last_error = _er
                lines = _md_dict.get(key)
                #lineno = _er.lineno
                msglst = ['in file: {}'.format(infilea)]
                msglst.append(str(_er))
                start = _er.lineno - 3
                if_start = {True: 0, False: start, }
                end = _er.lineno + 3
                start = if_start.get(start < 0)
                if_end = {True: len(lines) - 1, False: end, }
                end = if_end.get(end > len(lines) - 1)
                msglst += (
                    lines[i].split('\n')[0]
                    for i in range(start, _er.lineno-2))
                msglst.append(r'\/\/\/\/\/\/\/\/\/')
                msglst.append(lines[_er.lineno-1].split('\n')[0])
                msglst.append(r'^^^^^^^^^^^^^^^^^^')
                msglst += (
                    lines[i].split('\n')[0]
                    for i in range(_er.lineno, end))

                #msg = '\n'.join(msglst)
                print('\n'.join(msglst))
                return False

            assert len(dom_trees[key].getElementsByTagName('metadata')) == 1, \
                'Only one <metadata></metadata> sequence allowed here'
            [mde] = dom_trees[key].getElementsByTagName('metadata')
            if first and not self.repeater:
                if mde.getAttribute('repeater'):
                    if '-887354' in mde.getAttribute('repeater'):
                        repeater = mde.getAttribute('repeater').split('-')[0]
                        self.repeater = repeater
            self.accum.repeater_ctrl_type = self.repeater

            _child_files = []
            for _fl in mde.getElementsByTagName('filelist'):
                _child_files += [
                    _.firstChild.data for _ in _fl.getElementsByTagName('file')]

            def first_true(_child_files):
                """first_true(_child_files)

                Processing of _child_files if first is True
                """
                for _ in _child_files:
                    self.accum.add_file(os.path.join(self.fileinfo[DP], _))

            def first_false(_child_files):
                """first_false(_child_files)

                Processing of _child_files if first is False
                """
                if self._child_file_warning and _child_files:
                    print(
                        'The <filelist> field is ignored in '
                        + 'child files\nthe following are ignored ')
                    self._child_file_warning = False
                if _child_files:
                    print('child file: {}: {}' .format(infilea, _child_files))
                    LOGGER.error(
                        'Child files cannot include child files, detected %s',
                        _child_files)

            if first:
                first_true(_child_files)
            else:
                first_false(_child_files)

            for _s in mde.getElementsByTagName('slot'):
                datal = ['\n{} defined by {}\n\n'.format(
                    self.line_dict[CMT], os.path.relpath(infilea, start=self.fileinfo[1]))]
                for _ in _s.childNodes:
                    datal += [
                        ln.strip() +
                        '\n' for ln in _.data.split('\n') if ln.strip()]
                self.accum.add_slot(
                    slot.Slot(int(_s.getAttribute('id')), datain=datal))
        return True

    def doit(self, outfile, infilea=None):
        """doit(outfile)

        outfile is the output path.
        infilea is the input path unless testing

        """
        
        def _setup(_f):
            """_setup(_f)

            _f is a file path,

            Used to read a child file and initialize the processing
            of any XML within that file.
            If no XML in that file, the file contents are added to the next
            available unused slot less than 99
            """
            
            LOGGER.info('Processing child file: %s', _f)

            _line_dict = read_the_file(_f, self.line_dict[CMT])
            msg = 'File: {}, lines read: {}'.format(_f, len(_line_dict[INL]))
            LOGGER.debug(msg)
            _md_dict = gen_xml(_line_dict)
            gendocok = False
            if _md_dict:
                gendocok = self.gendocs(_md_dict, infile=_f)

            if not _md_dict or not gendocok:
                _highslot = sorted(self.accum.slots.keys())[-2:-1][0]
                self.accum.add_slot(
                    slot.Slot(_highslot+1, [l for n, l in _line_dict[INL]]))

        copyonly = not self.md_dict
        while 1:
            if copyonly:
                break
            # process the master file
            self.gendocs(self.md_dict, first=True, infile=infilea)
            self.accum.disable_priv_slots()
            _file_list = self.accum.get_filelist()
            if self.accum.slots[SLOT_INITIAL].is_mt() \
                or self.accum.slots[SLOT_FINAL].is_mt() \
                    or len(_file_list) < 2:
                copyonly = True
                break

            _files_ok = True
            if len(_file_list) == 1:
                copyonly = True
                break

            for _fn in _file_list[1:]:
                _ = os.path.join(self.fileinfo[DP], _fn)
                if not (os.path.exists(_) and os.path.isfile(_)):
                    _files_ok = False
                    print('unable to find file: {}'.format(_))
                    LOGGER.error('%s not found', _)

            if not _files_ok:
                print('aborting...')
                LOGGER.error('Aborting')
                raise IOError

            for _ in _file_list[1:]:
                try:
                    print('Processing file: {}'.format(os.path.basename(_)))
                    _setup(os.path.join(self.fileinfo[DP], _))
                except IOError as _e:
                    print(_e)
            break

        _of = os.path.abspath(outfile)

        if copyonly:  # if no metadata
            with open(outfile, 'w') as ofil:
                ofil.writelines([l for n, l in self.line_dict[INL]])
            common_p = os.path.commonpath((self.fileinfo[FP], _of))
            _ip = ['.']
            _op = ['.']
            _ip.append(self.fileinfo[FP].split(common_p)[1])
            _op.append((_of.split(common_p)[1]))
            print('copy: '+''.join(_ip) + ' -> '+''.join(_op))

        else:
            with open(outfile, 'w') as ofil:
                ofil.writelines(
                    _decode_special_xml_char(self.accum.get_lines()))

            print(str(_of) + ' successfully saved')


def _main():
    """_main()

    """

    LF_HANDLER.setLevel(logging.DEBUG)
    LC_HANDLER.setLevel(logging.ERROR)
    LC_HANDLER.setFormatter(LC_FORMATTER)
    LF_HANDLER.setFormatter(LF_FORMATTER)
    THE_LOGGER.setLevel(logging.DEBUG)
    THE_LOGGER.addHandler(LF_HANDLER)
    THE_LOGGER.addHandler(LC_HANDLER)

    THE_LOGGER.info("""
    ****************************************************
    cmdfilebuilder executed as main
    ****************************************************""")
    LOGGER.setLevel(logging.DEBUG)

    _parser = argparse.ArgumentParser(
        description='Generate an ordered text file'
        + 'in accordance to metadata in specified files')
    _parser.add_argument(
        'infile', default='sys.stdin', action='store',
        help='input text file name')
    _parser.add_argument(
        'outfile', default='sys.stdout', action='store',
        help='output file name')
    _parser.add_argument(
        '-li', '--loginfo',
        help='enable INFO logging',
        action="store_true")
    _parser.add_argument(
        '-ld', '--logdebug',
        help='enable DEBUG logging',
        action="store_true")

    # print(os.path.abspath('.'))
    THE_LOGGER.info('Current Path is: %s', str(os.path.abspath('.')))
    args = _parser.parse_args()
    _ = [
        THE_LOGGER.info('args:%s, %s', i[0], i[1])
        for i in vars(args).items()]

    if args.logdebug:
        LC_HANDLER.setLevel(logging.DEBUG)
    elif args.loginfo:
        LC_HANDLER.setLevel(logging.INFO)
    inf = args.infile
    outf = args.outfile
    print('processing {} -> {}' .format(inf, outf))

    try:
        with open(inf, 'r'):  # check file exists
            pass
    except IOError as _e:
        print(_e.args)
        print('Input file {} does not exist'.format(inf))
        THE_LOGGER.error('Input file %s does not exist', inf)
        raise _e

    try:
        with open(outf, 'r'):
            if not input('Output file exists, Overwrite? Y/N >').strip() \
               in ('Y', 'y', 'yes', 'Yes'):
                THE_LOGGER.info('User Canceled at output file exists')
                raise ValueError('User Canceled')
    except IOError:
        pass

    _cb = Cmdfilebuilder(inf)
    _cb.doit(outf, infilea=inf)


if __name__ == '__main__':
    try:
        _main()
        print("Success")
        THE_LOGGER.info("""
    *****************************
    Success
    *****************************        
        """)
    except IOError as ioe:
        THE_LOGGER.exception(ioe)
        print('cmdfilebilder.py io error')
    except ValueError as _:
        THE_LOGGER.exception(_)
        print(_)
