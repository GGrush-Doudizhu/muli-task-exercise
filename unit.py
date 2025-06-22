from eudplib import *


def modify_hero_to_normal_unit():
    UNITS_TO_MODIFY = {
        "Devouring One (Zergling)": "Zerg Zergling",
        "Hunter Killer (Hydralisk)": "Zerg Hydralisk",
        "Kukulza (Mutalisk)": "Zerg Mutalisk",
        # scourge
        "Jim Raynor (Marine)": "Terran Marine",
        "Gui Montag (Firebat)": "Terran Firebat",
        # medic
        "Jim Raynor (Vulture)": "Terran Vulture",
        "Edmund Duke (Tank Mode)": "Terran Siege Tank (Tank Mode)",
        "Edmund Duke (Siege Mode)": "Terran Siege Tank (Siege Mode)",
        "Fenix (Zealot)": "Protoss Zealot",
        "Fenix (Dragoon)": "Protoss Dragoon",
        "Tassadar (Templar)": "Protoss High Templar",
        # shuttle
        "Warbringer (Reaver)": "Protoss Reaver",
        "Raszagal (Corsair)": "Protoss Corsair",
        "Artanis (Scout)": "Protoss Scout",
    }

    PROPERTIES_TO_COPY = [
        "maxHp",
        "maxShield",
        "armor",
        "groundWeapon",
        "airWeapon",
    ]

    for hero_name, target_name in UNITS_TO_MODIFY.items():
        # hero, target = TrgUnit(hero), TrgUnit(target)
        # hero.groundWeapon = target.groundWeapon
        # hero.airWeapon = target.airWeapon
        # hero.maxHp = target.maxHp
        # hero.maxShield = target.maxShield
        hero = TrgUnit(hero_name)
        target = TrgUnit(target_name)
        for prop_name in PROPERTIES_TO_COPY:
            value_to_copy = getattr(target, prop_name)
            setattr(hero, prop_name, value_to_copy)