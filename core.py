from eudplib import *
from config import *


def set_player_type_to_human():
    actions = []

    for player in AI_PLAYER_IDS:
        actions.append(SetMemoryXEPD(EPD(0X57EEE0) + 9 * player + 0x2, SetTo, 2, 0xFF))

    DoActions(actions)


def is_single_player_Mode():
    return Memory(0x57F0B4, Exactly, 0)


def defeat_if_single_player_mode():
    if EUDIf()(is_single_player_Mode()):
        f_setcurpl(HUMAN_PLAYER)
        f_eprintln("\x06请在局域网或者战网玩！\x04为了防止输入单机作弊码，禁止使用单人模式游玩。")
        DoActions(Defeat())
    EUDEndIf()


def unset_men_groupFlags():
    for unit in UNSET_MEN_GROUPFLAGS_LIST:
        TrgUnit(unit).groupFlags.Men = 0


def stop_overlord():
    actions = []

    for player in AI_PLAYER_IDS:
        actions.append(MoveLocation("loc", "Zerg Overlord", player, "Anywhere"))
        actions.append(MoveUnit(1, "Zerg Overlord", player, "loc", "loc"))
    
    DoActions(actions)
        