#!/usr/bin/env python3
"""slot.py

    ------
    Slots
    ------
    There are 100 slots where slots 0 and 99 are special.
    Slots 1-98 contain lists of text that have been assigned to that slot
    (the output order of the list within each slot is undefined).

    Slots 0 and 99 contain lists with at most one element.
"""
import logging
import logging.handlers
from typing import Any, Union, Tuple, Callable, TypeVar, Generic, Sequence, Mapping, List, Dict, Set, Deque

LOGGER = logging.getLogger(__name__)
LOG_DIR = '../logs'
LOG_FILE = '/slot'


class Slot:
    """Slot

    A class that contains a list of strings that are to be output
    when the slot is sequenced
    """

    def __init__(self, slotid: int, datain: List[str] = None):
        """SLOT(slotid,datain=None)

        slotid is must be an integer with values between 0 and 99
        datain is a list of strings
        
        raises Value Error if illegal slot number

        """
        if slotid < 0 or slotid > 99:
            raise ValueError("slotid must be between 0 and 99 inclusive")
        self.ident: int = 0
        self.ident:int = slotid
        self.data: List[str] = []
        if datain:
            self.data = datain[:]

    def __str__(self):
        result:str=f'[id:{str(self.ident)}, len:{str(len(self.data))}, d:'
        while True:
            try:
                if not self.data:                    
                    break
                _t_data:List[str] = []
                
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
                _outl=['(']
                _outl.append(', '.join(_t_data))
                _outl.append(')')
                result=f'{result}{"".join(_outl)}'
                break 
            finally:
                result=f'{result}]'
        return result
        

    def append(self, _datain:Any):
        """append(datain)

        Appends a string or list to the slot's data
        """
        if isinstance(_datain, str):
            temp: str = _datain
            self.data.append(temp)
        elif isinstance(_datain, (list, tuple)):
            temp: List[Tuple[Any, ...]] = _datain
            self.data += temp
        else:
            assert False, 'bad argument'

    def is_mt(self) -> bool:
        """is_mt()

        returns True if the slot does not contain data (it is empty)
        False otherwise
        """
        return not self.data
