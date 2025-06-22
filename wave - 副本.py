from eudplib import *
import timer as t
from eud_helper import *


WAVE_CONFIGS = [
    {
        "ai_unit_num": 6,
        "ai_unit_name": "Zerg Zergling",
        "player_unit_num": 4,
        "player_unit_name": "Terran Marine",
    },
    # {
    #     "ai_unit_num": [6, 2],
    #     "ai_unit_name": ["Zerg Zergling", "Zerg Hydralisk"],
    #     "player_unit_num": [4, 1],
    #     "player_unit_name": ["Terran Marine", "Terran SCV"],
    # },
    # {
    #     "ai_unit_num": ,
    #     "ai_unit_name": ,
    #     "player_unit_num": ,
    #     "player_unit_name": ,
    # },
    # {
    #     "ai_unit_num": ,
    #     "ai_unit_name": ,
    #     "player_unit_num": ,
    #     "player_unit_name": ,
    # },
    # {
    #     "ai_unit_num": ,
    #     "ai_unit_name": ,
    #     "player_unit_num": ,
    #     "player_unit_name": ,
    # },
    # {
    #     "ai_unit_num": ,
    #     "ai_unit_name": ,
    #     "player_unit_num": ,
    #     "player_unit_name": ,
    # },
    {
        "ai_unit_num": 6,
        "ai_unit_name": "Zerg Zergling",
        "player_unit_num": 1,
        "player_unit_name": "Terran Vulture",
    },
    {
        "ai_unit_num": 2,
        "ai_unit_name": "Protoss Zealot",
        "player_unit_num": 1,
        "player_unit_name": "Terran Vulture",
    },
]


HUMAN = P2
AI = P1


ai_unitgroup = UnitGroup(12)
player_unitgroup = UnitGroup(12)


wave_index = EUDVariable()
reset = EUDLightBool()
is_end = EUDLightBool()


class WaveStruct(EUDStruct):
    _fields_ = [
        "ai_unit_num",
        "ai_unit_name",
        "player_unit_num",
        "player_unit_name",
    ]


init_values = []
for data in WAVE_CONFIGS:
    values = []
    for key in WaveStruct._fields_:
        value = data[key]
        if isinstance(value, str) and key.endswith("unit_name"):
            values.append(EncodeUnit(value))
        elif isinstance(value, int):
            values.append(value)
    init_values.append(WaveStruct(_static_initval=values))

wave_array = EUDArray(init_values)


def wave_manager():
    if RunIf(is_end.IsCleared()):
        RawTrigger(
            conditions=Bring(HUMAN, Exactly, 0, "Men", "battlefield"),
            actions=[
                RemoveUnitAt(All, "Men", "battlefield", AllPlayers),
                reset.Set(),
            ]
        )

        if RunIf(reset.IsSet()):
            if RunIf(wave_index <= len(WAVE_CONFIGS) - 1):
                wave = WaveStruct.cast(wave_array[wave_index])
                # wave = wave_array[wave_index]
                DoActions(
                    CreateUnit(wave.ai_unit_num, wave.ai_unit_name, "ai_unit_spawn_loc", AI),
                    reset.Clear(),
                )

                for _ in EUDLoopRange(wave.player_unit_num):
                    cunit = CUnit.create(wave.player_unit_name, "player_unit_spawn_loc", HUMAN)
                    player_unitgroup.add(cunit)
                    supplyUsed = TrgUnit(wave.player_unit_name).supplyUsed
                    HUMAN.zergControlUsed += -supplyUsed
                    HUMAN.terranSupplyUsed += -supplyUsed
                    HUMAN.protossPsiUsed += -supplyUsed
            if RunElse():
                DoActions(is_end.Set())
            RunEndIf()
        RunEndIf()

        RawTrigger(
            conditions=Bring(AI, Exactly, 0, "Men", "battlefield"),
            actions=[
                wave_index.AddNumber(1),
                RemoveUnitAt(All, "Men", "battlefield", AllPlayers),
                reset.Set(),
            ]
        )

        for cunit in EUDLoopPlayerCUnit(AI):
            EUDContinueIf(cunit.order == EncodeUnitOrder("Die"))
            dmin, nearest_unit = set_new_var(0xFFFF, 0)
            x0, y0 = cunit.posX, cunit.posY
            for unit in player_unitgroup.cploop:
                for dead in unit.dying:
                    unit.move_cp(0x64 // 4)
                    supplyUsed = TrgUnit(f_wread_cp(0, 0)).supplyUsed
                    HUMAN.zergControlUsed += supplyUsed
                    HUMAN.terranSupplyUsed += supplyUsed
                    HUMAN.protossPsiUsed += supplyUsed
                # pos
                unit.move_cp(0x28 // 4)
                x, y = f_posread_cp(0)
                dis = (x - x0).iabs() + (y - y0).iabs()
                EUDContinueIf(dis >= dmin)
                nearest_unit << unit.epd
                dmin << dis

            if RunIf(nearest_unit != 0):
                ctarget = CUnit.cast(nearest_unit)
                cunit.order = "Attack Unit"
                cunit.orderTarget = ctarget
                cunit.orderTargetPos = ctarget.pos
            RunEndIf()

    RunEndIf()