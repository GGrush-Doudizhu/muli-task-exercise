from eudplib import *


frame = EUDVariable()
sec = EUDVariable()


def clock():
    RawTrigger(
        conditions=frame.AtMost(23),
        actions=[
            frame.AddNumber(1),
        ]
    )
    RawTrigger(
        conditions=frame.AtLeast(24),
        actions=[
            frame.SetNumber(0),
            sec.AddNumber(1),
        ]
    )
