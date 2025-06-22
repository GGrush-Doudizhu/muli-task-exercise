from eudplib import *
# import timer as t
from eud_helper import *


# --- Configuration ---

HUMAN = P2
AI = P1

WAVE_CONFIGS_PY = [
    # vulture vs Zergling
    {
        "ai_units": [
            {"name": "Zerg Zergling", "num": 6}, # speed_upgrade is omitted, defaults to False
        ],
        "player_units": [
            {"name": "Terran Vulture", "num": 1},
        ],
    },
    # vulture vs speed Zergling
    {
        "ai_units": [
            {"name": "Zerg Zergling", "num": 12, "speed_upgrade": True},
        ],
        "player_units": [
            {"name": "Terran Vulture", "num": 2},
        ],
    },
    # vulture vs zealot + marine
    {
        "ai_units": [
            {"name": "Protoss Zealot", "num": 2},
            {"name": "Terran Marine", "num": 6},
        ],
        "player_units": [
            {"name": "Terran Vulture", "num": 3, "speed_upgrade": True},
        ],
    },
    # marine vs zealot
    {
        "ai_units": [
            {"name": "Protoss Zealot", "num": 1},
        ],
        "player_units": [
            {"name": "Terran Marine", "num": 3},
        ],
    },
    # marine + scv vs zealot
    {
        "ai_units": [
            {"name": "Protoss Zealot", "num": 2},
        ],
        "player_units": [
            {"name": "Terran Marine", "num": 3},
            {"name": "Terran SCV", "num": 2},
        ],
    },
    # marine vs zergling
    {
        "ai_units": [
            {"name": "Zerg Zergling", "num": 6},
        ],
        "player_units": [
            {"name": "Terran Marine", "num": 5},
        ],
    },
    # marine + scv vs zergling
    {
        "ai_units": [
            {"name": "Zerg Zergling", "num": 6},
        ],
        "player_units": [
            {"name": "Terran Marine", "num": 2},
            {"name": "Terran SCV", "num": 4},
        ],
    },
]


# --- Global Variables & Data Structures ---

wave_index = EUDVariable()
reset = EUDLightBool()
is_end = EUDLightBool()

ai_unitgroup = UnitGroup(24)
player_unitgroup = UnitGroup(24)

# MODIFIED: Added 'apply_speed_upgrade' field to the struct
class UnitGroupInfo(EUDStruct):
    _fields_ = [
        "unit_id",
        "unit_num",
        "apply_speed_upgrade", # 0 for False, 1 for True
    ]

class WaveConfig(EUDStruct):
    _fields_ = [
        "ai_groups_ptr",
        "ai_groups_count",
        "player_groups_ptr",
        "player_groups_count",
    ]


# --- Data Initialization (Compile-time) ---

wave_configs_list = []
for wave_data in WAVE_CONFIGS_PY:
    # Process AI unit groups
    ai_groups_py = wave_data["ai_units"]
    ai_unit_groups_data = [
        # MODIFIED: Read the 'speed_upgrade' flag. Use .get() to default to False if omitted.
        UnitGroupInfo(_static_initval=[
            EncodeUnit(g["name"]),
            g["num"],
            g.get("speed_upgrade", False)
        ])
        for g in ai_groups_py
    ]
    ai_groups_array = EUDArray(ai_unit_groups_data)
    
    # Process Player unit groups
    player_groups_py = wave_data["player_units"]
    player_unit_groups_data = [
        # MODIFIED: Read the 'speed_upgrade' flag. Use .get() to default to False if omitted.
        UnitGroupInfo(_static_initval=[
            EncodeUnit(g["name"]),
            g["num"],
            g.get("speed_upgrade", False)
        ])
        for g in player_groups_py
    ]
    player_groups_array = EUDArray(player_unit_groups_data)
    
    # Create the final WaveConfig object
    wave_configs_list.append(
        WaveConfig(_static_initval=[
            ai_groups_array,
            len(ai_groups_py),
            player_groups_array,
            len(player_groups_py),
        ])
    )

WAVE_CONFIGS = EUDArray(wave_configs_list)


# --- Main Game Logic Function ---

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
            if RunIf(wave_index.AtMost(len(WAVE_CONFIGS_PY) - 1)):
                wave_config = WaveConfig.cast(WAVE_CONFIGS[wave_index])
                
                # Spawn AI units
                for i in EUDLoopRange(wave_config.ai_groups_count):
                    group_info = UnitGroupInfo.cast(f_dwread_epd(wave_config.ai_groups_ptr + i))
                    for _ in EUDLoopRange(group_info.unit_num):
                        cunit = CUnit.create(group_info.unit_id, "ai_unit_spawn_loc", AI)
                        ai_unitgroup.add(cunit)
                        # MODIFIED: Apply speed upgrade immediately after creation if flagged
                        if EUDIf()(group_info.apply_speed_upgrade == 1):
                            cunit.set_speed_upgrade()
                        EUDEndIf()


                # Spawn Player units
                for i in EUDLoopRange(wave_config.player_groups_count):
                    group_info = UnitGroupInfo.cast(f_dwread_epd(wave_config.player_groups_ptr + i))
                                      
                    for _ in EUDLoopRange(group_info.unit_num):
                        unit = TrgUnit(group_info.unit_id)
                        cunit = CUnit.create(unit, "player_unit_spawn_loc", HUMAN)
                        player_unitgroup.add(cunit)

                        # MODIFIED: Apply speed upgrade immediately after creation if flagged
                        if EUDIf()(group_info.apply_speed_upgrade == 1):
                            cunit.set_speed_upgrade()
                        EUDEndIf()
                        
                        supplyUsed = unit.supplyUsed
                        EUDSwitch(unit.groupFlags, 0x7)
                        if EUDSwitchCase()(1):
                            HUMAN.zergControlUsed += -supplyUsed
                            EUDBreak()
                        if EUDSwitchCase()(2):
                            HUMAN.terranSupplyUsed += -supplyUsed
                            EUDBreak()
                        if EUDSwitchCase()(4):
                            HUMAN.protossPsiUsed += -supplyUsed
                            EUDBreak()
                        EUDEndSwitch()
                    
                DoActions(reset.Clear())

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

        for player_unit in ai_unitgroup.cploop:
            for player_dead in player_unit.dying:
                pass

            player_cunit = CUnit.cast(player_unit.epd)
            dmin, nearest_unit = set_new_var(0xFFFF, 0)
            x0, y0 = player_cunit.posX, player_cunit.posY
            for ai_unit in player_unitgroup.cploop:
                for ai_dead in ai_unit.dying:
                    ai_unit.move_cp(0x64 // 4)
                    unitType = TrgUnit(f_wread_cp(0, 0))
                    supplyUsed = unitType.supplyUsed
                    EUDSwitch(unitType.groupFlags, 0x7)
                    if EUDSwitchCase()(1):
                        HUMAN.zergControlUsed += supplyUsed
                        EUDBreak()
                    if EUDSwitchCase()(2):
                        HUMAN.terranSupplyUsed += supplyUsed
                        EUDBreak()
                    if EUDSwitchCase()(4):
                        HUMAN.protossPsiUsed += supplyUsed
                        EUDBreak()
                    EUDEndSwitch()
                # pos
                ai_unit.move_cp(0x28 // 4)
                x, y = f_posread_cp(0)
                dis = (x - x0).iabs() + (y - y0).iabs()
                EUDContinueIf(dis >= dmin)
                nearest_unit << ai_unit.epd
                dmin << dis

            if RunIf(nearest_unit != 0):
                ctarget = CUnit.cast(nearest_unit)
                player_cunit.order = "Attack Unit"
                player_cunit.orderTarget = ctarget
                player_cunit.orderTargetPos = ctarget.pos
            RunEndIf()
            
    RunEndIf()