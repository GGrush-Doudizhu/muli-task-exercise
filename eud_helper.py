# eud_helper.py
from eudplib import *
from eudplib.epscript.helper import _RELIMP, _TYGV, _TYSV, _TYLV, _CGFW, _ARR, _VARR, _SRET, _SV, _ATTW, _ARRW, _ATTC, _ARRC, _L2V, _LSH, _ALL
from enum import IntEnum


def set_new_var(*values):
    ret, ops = [], []
    for value in values:
        new_var = EUDVariable()
        ops.append((new_var, SetTo, value))
        ret.append(new_var)
    NonSeqCompute(ops)
    return ret


# --- extend TrgPlayer ---
class _UnitDataProxy:
    def __init__(self, base_epd, player_index, unit_multiplier=12):
        self._base_epd = base_epd
        self._player_index = player_index
        self._unit_multiplier = unit_multiplier

    def _get_target_epd(self, unit):
        unit_index = EncodeUnit(unit)
        return self._base_epd + unit_index * self._unit_multiplier + self._player_index

    def __getitem__(self, unit):
        return f_dwread_epd(self._get_target_epd(unit))

    def __setitem__(self, unit, value):
        f_dwwrite_epd(self._get_target_epd(unit), value)


def create_playerUnit_data_proxy_getter(base_address, unit_multiplier=12):
    base_epd = EPD(base_address)
    
    def getter(self):
        player_index = self._value
        return _UnitDataProxy(base_epd, player_index, unit_multiplier)
    
    return getter


TrgPlayer.allUnitCount = property(create_playerUnit_data_proxy_getter(0x582324))
TrgPlayer.completedUnitCount = property(create_playerUnit_data_proxy_getter(0x584DE4))


# --- EUDIf ---
def RunOr(*conditions):
    """
    A wrapper for EUDSCOr.
    """
    if not conditions:
        return Always()
    
    sc_or = EUDSCOr()
    for cond in conditions:
        sc_or = sc_or(cond)
    return sc_or()


def RunAnd(*conditions):
    """
    A wrapper for EUDSCAnd.
    """
    if not conditions:
        return Always()

    sc_and = EUDSCAnd()
    for cond in conditions:
        sc_and = sc_and(cond)
    return sc_and()


def RunIf(condition):
    """
    A simplified, efficient `EUDIf()()` statement.
    """
    return EUDIf()(condition)

def RunElif(condition):
    """
    A simplified, efficient `EUDElseIf()()` statement.
    """
    return EUDElseIf()(condition)


RunElse = EUDElse()
RunEndIf = EUDEndIf


# --- extend CUnit ---
def _cunit_create(cls, unit, location, player):
    ret = cls.from_next()
    DoActions(CreateUnit(1, unit, location, player))
    return ret

CUnit.create = classmethod(_cunit_create)


class RunOnce:
    def __init__(self, condition=None):
        self.condition = condition

    def __enter__(self):
        execute_once_obj = EUDExecuteOnce()
        if self.condition is None:
            execute_once_obj()
        else:
            execute_once_obj(self.condition)
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        EUDEndExecuteOnce()
        return False