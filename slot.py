#!/usr/bin/env python3
"""slot.py

    ------
    Slots
    ------
    There are 100 slots where slots 0 and 99 are special.
    Slots 1-98 contain lists of text that have been assigned to that slot (
    the output order of the list within each slot is undefined).

    Slots 0 and 99 contain lists with at most one element.
"""
import logging
import logging.handlers

LOGGER = logging.getLogger(__name__)
LOG_DIR = '../logs'
LOG_FILE = '/slot'

class Slot:
    """Slot

    A class that contains a list of strings that are to be output
    when the slot is sequenced
    """
    def __init__(self, slotid, datain=None):
        """SLOT(slotid,datain=None)

        Slot is must be an integer with values between 0 and 99
        datain is a list of strings

        """
        self.ident = 0
        self.ident = slotid
        self.data = []
        if datain:
            self.data = datain[:]

    def __str__(self):
        _outl = ['[']
        _outl.append('id:')
        _outl.append(str(self.ident))
        _outl.append(', len:')
        _outl.append(str(len(self.data)))
        _outl.append(', d:')
        if not self.data:
            _outl.append(']')
            return ''.join(_outl).strip()
        _t_data = []
        for _ in self.data:
            if len(_) < 10:
                _t_data.append(_)
            else:
                _t_data.append(_[0:5] + ' ... ' + _[-2:])

        if len(_t_data) > 5:
            _j = []
            _j += _t_data[0:1]
            _j.append(' (...) ')
            _j += _t_data[-2:]
            _t_data = _j

        _outl.append('(')
        _outl.append(', '.join(_t_data))
        _outl.append(')')
        _outl.append(']')
        return ''.join(_outl)

    def append(self, _datain):
        """append(datain)

        Appends a string or list to the slot's data
        """
        if isinstance(_datain, str):
            self.data.append(_datain)
        elif isinstance(_datain, (list, tuple)):
            self.data += _datain
        else:
            assert False, 'bad argument'

    def is_mt(self):
        """is_mt()

        returns True if the slot does not contain data (is empty)
        False otherwise
        """
        if self.data:
            return False

        return True
