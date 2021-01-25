#!/usr/bin/env python3
"""accumulator.py

Gathers the metadata as processed in cmdfilebuilder
and organizes it by slots and files

Copyright (C) Daniel B. Curtis 2015-2021, Distributed under version 3 of the GNU GENERAL PUBLIC LICENSE

"""

import os
import datetime
import re
from typing import Any, Tuple, List, Dict, Set
import logging
import logging.handlers
from slot import Slot
from constants import SLOT_FINAL, SLOT_INITIAL

PAT = re.compile(r'(\n\s*\n)+\s*\n', re.MULTILINE | re.DOTALL)

LOGGER = logging.getLogger(__name__)
LOG_DIR = '../logs'
LOG_FILE = '/accumulator'


class Accumulator:
    """Accumulator(cmt)

    the cmt is the comment text for the system.
    """

    def __init__(self, cmt):
        """Accumulator(cmt)

        cmt is the comment flag
        """
        self._cmt = cmt
        self._fileset: Set[str] = set()
        self._filelist: List[str] = []
        self.slots: Dict[int, Any] = {}
        self.slots[SLOT_INITIAL] = Slot(SLOT_INITIAL)
        self.slots[SLOT_FINAL] = Slot(SLOT_FINAL)
        self._disableprivslots: bool = False
        self.repeater_ctrl_type = 'Unknown'

    def disable_priv_slots(self):
        """disable_priv_slots()

        disables additions to slots 0 and 99
        """
        self._disableprivslots = True

    def get_fileset(self) -> Set[Any]:
        """get_fileset()

        returns the file set.
        """
        return {l for l in self._fileset}  # relturning copy of the set

    def add_file(self, _fin: str) -> bool:
        """add_file(f)

        if the file is already in the fileset, will return False
        otherwise the file will be added to the fileset and return True
        """
        _f = os.path.abspath(_fin)
        if _f in self._fileset:
            return False

        self._fileset.add(_f)
        self._filelist.append(_f)
        return True

    def get_filelist(self, full_path: bool = False) -> List[Any]:
        """get_filelist()

        returns the filelist.  If full_path True, the full absolute path is provided
        if full_path=false, the common paths of the files in the file list are removed.
        """
        if full_path:
            return self._filelist[:]

        if not self._filelist:
            return[]

        if len(self._filelist) == 1:
            return [os.path.basename(n) for n in self._filelist]
        common = os.path.join(os.path.commonpath(self._filelist), '')
        stripped = [_.split(common)[1] for _ in self._filelist]
        assert len(set(stripped)) == len(stripped)
        return stripped

    def add_slot(self, _myslot: int):
        """add_slot(_myslot)

        If a slot with the same id is already defined, the contents of _myslot is appended
        onto the existing slot.  Otherwise, _myslot is saved in the self.slots dict

        If _disableprivslots and s0 or s99, nothing is done
        """
        
        if self._disableprivslots and _myslot.ident in (SLOT_INITIAL, SLOT_FINAL):
            LOGGER.error('Attempt to define slot 0 or 99 in non-primary file')
            return

        if _myslot.ident in self.slots:
            self.slots[_myslot.ident].data += _myslot.data
        else:
            LOGGER.info('slot %s defined', _myslot.ident)
            self.slots[_myslot.ident] = _myslot

    def get_lines(self) -> List[str]:
        """get_lines()

        Generates lines from the slots.
        Labels the slot seperations
        returns a list of lines in slot order
        """

        keys = sorted(self.slots.keys())
        result: List[str] = []
        _jj: str = ""
        if self._filelist:
            _jj = self._filelist[0:1][0]

        if not _jj.strip():
            _jj = '!UNSPECIFIED!'

        result.append(
            f'{self._cmt} created on: {str(datetime.datetime.now())[0:-7]}\n')
        result.append(
            f'{self._cmt} Controller type:{self.repeater_ctrl_type}\n')
        result.append(f'{self._cmt} result from processing {_jj}\n')
        if self.get_filelist():
            result.append(f'{self._cmt} Files included by reference:\n')
            result += [f'{self._cmt}\t{_n}\n' for _n in self.get_filelist()]
        for _k in keys:
            result.append(f'\n{self._cmt}lines from Slot {str(_k)}\n\n')
            result += self.slots[_k].data

        result = [
            l + '\n' for l in re.sub(PAT, '\n\n', ''.join(result)).split('\n')]

        return result
