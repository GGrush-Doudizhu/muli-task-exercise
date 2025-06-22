from eudplib import *
from eud_helper import *
import core as c
import unit as u
import wave as w
import timer as t


def onPluginStart():
    c.set_player_type_to_human()
    u.modify_hero_to_normal_unit()



def beforeTriggerExec():
    w.wave_manager()


def afterTriggerExec():
    t.clock()
