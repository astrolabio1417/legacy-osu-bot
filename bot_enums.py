from enum import Enum, IntEnum


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
