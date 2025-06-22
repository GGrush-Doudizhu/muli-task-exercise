from eudplib import *
from eud_helper import *
import struct
import wave as w


@EUDFunc
def get_loc_xy(loc):
    loc = EncodeLocation(loc)
    loc *= 5
    VProc(loc, [loc.AddNumber(EPD(0x58DC4C)), loc.SetDest(EPD(0x6509B0))])
    x = f_dwread_cp(0)
    DoActions(SetMemory(0x6509B0, Add, 1))
    f_dwread_cp(0, ret=[loc])
    DoActions(SetMemory(0x6509B0, Add, 1))
    x += f_dwread_cp(0)
    DoActions(SetMemory(0x6509B0, Add, 1))
    loc += f_dwread_cp(0)
    f_setcurpl2cpcache()
    return x // 2, loc // 2


@EUDFunc
def get_loc_pos(loc):
    x, y = get_loc_xy(loc)
    return x + f_bitlshift(y, 16)


