from typing import Literal
from enum import Enum


class TEAM_MODE(Enum):
    HEAD_TO_HEAD = ("HeadToHead", 0)
    TAG_COOP = ("TagCoop", 1)
    TEAM_VS = ("TeamVs", 2)
    TAG_VS = ("TagTeamVs", 3)


class SCORE_MODE(Enum):
    SCORE = ("Score", 0)
    ACCURACY = ("Accuracy", 1)
    COMBO = ("Combo", 2)
    SCORE_V2 = ("ScoreV2", 3)


class PLAY_MODE(Enum):
    OSU = ("osu!", 0)
    TAIKO = ("Taiko", 1)
    CATCH_THE_BEAT = ("Catch the Beat", 2)
    MANIA = ("osu!Mania", 3)


class BOT_MODE(Enum):
    AUTO_HOST = "AutoHost"
    AUTO_ROTATE_MAP = "AutoRotateMap"


class MESSAGE_YIELD(Enum):
    DISCONNECT = "DISCONNECT"
    RECONECTION_FAILED = "RECONECTION_FAILED"
    RECONNECTED = "RECONNECTED"


VALID_ROLES = [
    "Host",
    "TeamBlue",
    "TeamRed",
    "Hidden",
    "HardRock",
    "SuddenDeath",
    "Flashlight",
    "SpunOut",
    "NoFail",
    "Easy",
    "Relax",
    "Relax2",
]
