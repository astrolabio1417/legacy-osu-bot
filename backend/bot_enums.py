from enum import Enum, IntEnum


class TEAM_MODE(IntEnum):
    HEAD_TO_HEAD = 0
    TAG_COOP = 1
    TEAM_VS = 2
    TAG_VS = 3


class SCORE_MODE(IntEnum):
    SCORE = 0
    ACCURACY = 1
    COMBO = 2
    SCORE_V2 = 3


class PLAY_MODE(IntEnum):
    OSU = 0
    TAIKO = 1
    CATCH_THE_BEAT = 2
    MANIA = 3


class BOT_MODE(Enum):
    AUTO_HOST = "AutoHost"
    AUTO_ROTATE_MAP = "AutoRotateMap"


class MESSAGE_YIELD(Enum):
    DISCONNECT = "DISCONNECT"
    RECONECTION_FAILED = "RECONECTION_FAILED"
    RECONNECTED = "RECONNECTED"


class RANK_STATUS(IntEnum):
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4
    PENDING = 0
    WIP = -1
    GRAVEYARD = -2


class CHIMU_GENRE(IntEnum):
    GAME = 2
    ANIME = 3
    ROCK = 4
    POP = 5
    OTHER = 6
    NOVELTY = 7
    HIPHOP = 9
    ELECTRONIC = 10


class CHIMU_LANGUAGE(IntEnum):
    ENGLISH = 2
    JAPANESE = 3
    CHINESE = 4
    INSTRUMENT = 5
    KOREAN = 6
    FRENCH = 7
    GERMAN = 8
    SWEDISH = 9
    SPANISH = 10
    ITALIAN = 11
